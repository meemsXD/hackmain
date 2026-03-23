from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import log
from apps.users.models import Recycler, User

from .models import QR, QRScanLog, Status, Waste
from .serializers import (
    QRScanLogSerializer,
    QRScanSerializer,
    QRExtendSerializer,
    QRSerializer,
    StatusUpdateSerializer,
    WasteCreateSerializer,
    WasteSerializer,
)


FINAL_STATES = {'ACCEPTED', 'CANCELLED'}
ROLE_ALLOWED_STATE_UPDATES = {
    'DRIVER': {'IN_TRANSIT', 'DELIVERED'},
    'MEDICAL': {'ACCEPTED'},
    'RECYCLER': {'CANCELLED'},
    'ADMIN': {choice[0] for choice in Status.STATE_CHOICES},
}
ALLOWED_TRANSITIONS = {
    'CREATED': {'IN_TRANSIT', 'CANCELLED'},
    'IN_TRANSIT': {'DELIVERED', 'CANCELLED'},
    'DELIVERED': {'ACCEPTED', 'CANCELLED'},
    'ACCEPTED': set(),
    'CANCELLED': set(),
}


def _base_waste_queryset():
    return Waste.objects.select_related('medical_organization', 'delivery_point', 'qr').prefetch_related('statuses')


def _is_admin(user) -> bool:
    return bool(user and (user.role == 'ADMIN' or user.is_superuser))


def _is_inspector(user) -> bool:
    return bool(user and user.role == 'INSPECTOR')


def _scoped_waste_queryset(user):
    queryset = _base_waste_queryset()

    if _is_admin(user) or _is_inspector(user):
        return queryset

    if user.role == 'RECYCLER':
        if user.organization_id:
            return queryset.filter(medical_organization__user__organization_id=user.organization_id)
        if user.medical_org_id:
            return queryset.filter(medical_organization_id=user.medical_org_id)
        return queryset.none()

    if user.role == 'MEDICAL':
        if user.organization_id:
            return queryset.filter(delivery_point__user__organization_id=user.organization_id)
        if user.recycler_profile_id:
            return queryset.filter(delivery_point_id=user.recycler_profile_id)
        return queryset.none()

    if user.role == 'DRIVER':
        if not user.driver_profile_id:
            return queryset.none()
        scoped = queryset.filter(delivery_point__drivers__id=user.driver_profile_id)
        if user.organization_id:
            scoped = scoped.filter(delivery_point__user__organization_id=user.organization_id)
        return scoped.distinct()

    return queryset.none()


def _medical_org_owner_org_id(waste: Waste):
    try:
        return waste.medical_organization.user.organization_id
    except User.DoesNotExist:
        return None


def _delivery_point_owner_org_id(waste: Waste):
    try:
        return waste.delivery_point.user.organization_id
    except User.DoesNotExist:
        return None


def _assert_batch_access(user, waste: Waste):
    if _is_admin(user) or _is_inspector(user):
        return

    if user.role == 'RECYCLER':
        if user.organization_id and _medical_org_owner_org_id(waste) == user.organization_id:
            return
        if user.medical_org_id == waste.medical_organization_id:
            return

    if user.role == 'MEDICAL':
        if user.organization_id and _delivery_point_owner_org_id(waste) == user.organization_id:
            return
        if user.recycler_profile_id == waste.delivery_point_id:
            return

    if user.role == 'DRIVER' and user.driver_profile_id and waste.delivery_point.drivers.filter(id=user.driver_profile_id).exists():
        if not user.organization_id:
            return
        if _delivery_point_owner_org_id(waste) == user.organization_id:
            return

    raise PermissionDenied('У вас нет доступа к этой партии.')


def _assert_qr_logs_access(user, waste: Waste):
    if _is_admin(user) or _is_inspector(user):
        return

    if user.role == 'RECYCLER':
        if user.organization_id and _medical_org_owner_org_id(waste) == user.organization_id:
            return
        if user.medical_org_id == waste.medical_organization_id:
            return

    if user.role == 'MEDICAL':
        if user.organization_id and _delivery_point_owner_org_id(waste) == user.organization_id:
            return
        if user.recycler_profile_id == waste.delivery_point_id:
            return

    raise PermissionDenied('Доступ к логу сканирований запрещен.')


def _validate_delivery_point_scope(user, delivery_point_id):
    if not delivery_point_id or user.role != 'RECYCLER' or not user.organization_id:
        return

    allowed = Recycler.objects.filter(pk=delivery_point_id, user__organization_id=user.organization_id).exists()
    if not allowed:
        raise ValidationError({'delivery_point': 'Можно выбрать переработчика только своей организации.'})


class WasteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return WasteCreateSerializer if self.request.method == 'POST' else WasteSerializer

    def get_queryset(self):
        return _scoped_waste_queryset(self.request.user)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not (_is_admin(user) or user.role == 'RECYCLER'):
            raise PermissionDenied('Создавать партии может только образователь или администратор.')

        payload = request.data.copy()
        if user.role == 'RECYCLER':
            if not user.medical_org_id:
                raise ValidationError({'medical_organization': 'У пользователя не заполнен профиль образователя.'})
            payload['medical_organization'] = str(user.medical_org_id)
            _validate_delivery_point_scope(user, payload.get('delivery_point'))

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        waste = serializer.save()

        log(
            user,
            'batch_created',
            'waste',
            waste.id,
            after={
                'waste_type': waste.waste_type,
                'quantity': str(waste.quantity),
                'medical_organization': waste.medical_organization_id,
                'delivery_point': waste.delivery_point_id,
            },
        )

        return Response(WasteSerializer(waste).data, status=status.HTTP_201_CREATED)


class WasteDetailView(generics.RetrieveAPIView):
    serializer_class = WasteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return _scoped_waste_queryset(self.request.user)


class StatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StatusUpdateSerializer

    def post(self, request, pk):
        waste = get_object_or_404(_base_waste_queryset(), pk=pk)
        _assert_batch_access(request.user, waste)

        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        next_state = serializer.validated_data['state']

        user = request.user
        role_allowed_states = ROLE_ALLOWED_STATE_UPDATES.get(user.role, set())
        if not _is_admin(user) and next_state not in role_allowed_states:
            raise PermissionDenied('Эта роль не может установить указанный статус.')

        current_state = waste.current_status or 'CREATED'
        if not _is_admin(user) and next_state not in ALLOWED_TRANSITIONS.get(current_state, set()):
            raise ValidationError({'state': f'Недопустимый переход статуса: {current_state} -> {next_state}.'})

        status_obj = Status.objects.create(
            waste=waste,
            state=next_state,
            changed_by=user if user.is_authenticated else None,
        )

        if next_state in FINAL_STATES and getattr(waste, 'qr', None):
            waste.qr.is_active = False
            waste.qr.save(update_fields=['is_active'])

        log(
            user,
            'batch_status_changed',
            'waste',
            waste.id,
            before={'state': current_state},
            after={'state': next_state, 'time': status_obj.time.isoformat()},
        )

        return Response({'state': status_obj.state, 'time': status_obj.time})


class QRDetailView(generics.RetrieveAPIView):
    serializer_class = QRSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        waste = get_object_or_404(_base_waste_queryset(), pk=self.kwargs['pk'])
        _assert_batch_access(self.request.user, waste)

        qr = get_object_or_404(QR, waste=waste)
        qr.deactivate_if_expired()
        return qr


class QRScanView(APIView):
    serializer_class = QRScanSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = QRScanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code'].strip()
        user = request.user if request.user.is_authenticated else None

        qr = (
            QR.objects.select_related('waste', 'waste__medical_organization', 'waste__delivery_point', 'waste__qr')
            .prefetch_related('waste__statuses')
            .filter(code=code)
            .first()
        )

        if not qr:
            QRScanLog.objects.create(raw_code=code, scanned_by=user, success=False, fail_reason='QR_NOT_FOUND')
            return Response({'detail': 'QR-код не найден.'}, status=status.HTTP_404_NOT_FOUND)

        qr.deactivate_if_expired()
        if not qr.is_active:
            reason = 'QR_EXPIRED' if qr.is_expired else 'QR_INACTIVE'
            QRScanLog.objects.create(qr=qr, raw_code=code, scanned_by=user, success=False, fail_reason=reason)
            detail = 'Срок действия QR-кода истек.' if reason == 'QR_EXPIRED' else 'QR-код деактивирован.'
            return Response({'detail': detail}, status=status.HTTP_403_FORBIDDEN)

        QRScanLog.objects.create(qr=qr, raw_code=code, scanned_by=user, success=True, fail_reason='')

        return Response({'batch': WasteSerializer(qr.waste).data, 'qr': QRSerializer(qr).data})


class QRScanLogListView(generics.ListAPIView):
    serializer_class = QRScanLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        waste = get_object_or_404(_base_waste_queryset(), pk=self.kwargs['pk'])
        _assert_qr_logs_access(self.request.user, waste)

        blocked_param = (self.request.query_params.get('blocked') or '1').lower()
        blocked_only = blocked_param not in {'0', 'false', 'no'}

        queryset = QRScanLog.objects.filter(qr__waste=waste).select_related('qr', 'scanned_by')
        if blocked_only:
            queryset = queryset.filter(success=False)
        return queryset


class QRExtendView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QRExtendSerializer

    def post(self, request, pk):
        waste = get_object_or_404(_base_waste_queryset(), pk=pk)
        user = request.user

        if not _is_admin(user):
            if user.role != 'RECYCLER' or user.medical_org_id != waste.medical_organization_id:
                raise PermissionDenied('Продлевать QR может только образователь-владелец или администратор.')

        qr = get_object_or_404(QR, waste=waste)

        serializer = QRExtendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        hours = serializer.validated_data['hours']

        base_time = qr.expires_at if qr.expires_at > timezone.now() else timezone.now()
        before = qr.expires_at

        qr.expires_at = base_time + timedelta(hours=hours)
        qr.is_active = True
        qr.save(update_fields=['expires_at', 'is_active'])

        log(
            user,
            'qr_extended',
            'qr',
            qr.id,
            before={'expires_at': before.isoformat() if before else None},
            after={'expires_at': qr.expires_at.isoformat(), 'hours_added': hours},
        )

        return Response(QRSerializer(qr).data)

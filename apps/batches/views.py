from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.access.services import extend_batch_token
from apps.access.models import TokenAccessAttempt
from apps.access.permissions import has_driver_access_to_batch
from apps.common.enums import BatchStatusChoices
from apps.roles.permissions import IsAdminRole
from apps.users.serializers import SignatureCheckMixin
from .permissions import IsEducator, IsProcessor
from .models import WasteBatch
from .serializers import WasteBatchSerializer, EducatorBatchCreateSerializer, EducatorBatchUpdateSerializer, BatchStatusHistorySerializer, ExtendTokenSerializer, BlockedAttemptSerializer
from .services import create_batch, update_batch, cancel_batch, accept_batch

class EducatorBatchListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsEducator]

    def get_queryset(self):
        qs = WasteBatch.objects.select_related('waste_type', 'creator_org', 'processor_org', 'current_driver', 'access_token').filter(creator_org=self.request.user.organization)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(batch_number__icontains=search)
        return qs

    def get_serializer_class(self):
        return EducatorBatchCreateSerializer if self.request.method == 'POST' else WasteBatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not SignatureCheckMixin.check(request.user, serializer.validated_data.pop('signature_token')):
            return Response({'detail': 'Неверный токен подписи'}, status=400)
        batch = create_batch(user=request.user, validated_data=serializer.validated_data, signature_user=request.user)
        return Response(WasteBatchSerializer(batch).data, status=201)

class EducatorBatchDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsEducator]

    def get_queryset(self):
        return WasteBatch.objects.select_related('waste_type', 'creator_org', 'processor_org', 'current_driver', 'access_token').filter(creator_org=self.request.user.organization)

    def get_serializer_class(self):
        return EducatorBatchUpdateSerializer if self.request.method in ['PATCH', 'PUT'] else WasteBatchSerializer

    def update(self, request, *args, **kwargs):
        batch = self.get_object()
        serializer = self.get_serializer(instance=batch, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data.copy()
        if not SignatureCheckMixin.check(request.user, data.pop('signature_token')):
            return Response({'detail': 'Неверный токен подписи'}, status=400)
        token_expires_at = data.pop('token_expires_at', None)
        if batch.status == BatchStatusChoices.CREATED:
            pass
        elif batch.status == BatchStatusChoices.IN_TRANSIT and not batch.delivered_at:
            for field in ['waste_type', 'quantity', 'unit', 'pickup_address']:
                data.pop(field, None)
        else:
            return Response({'detail': 'Редактирование недоступно для данного статуса'}, status=400)
        batch = update_batch(batch=batch, user=request.user, data=data)
        if token_expires_at:
            extend_batch_token(batch=batch, expires_at=token_expires_at)
        return Response(WasteBatchSerializer(batch).data)

class CancelBatchView(APIView):
    permission_classes = [IsEducator]

    def post(self, request, pk):
        batch = get_object_or_404(WasteBatch, pk=pk, creator_org=request.user.organization)
        if not SignatureCheckMixin.check(request.user, request.data.get('signature_token', '')):
            return Response({'detail': 'Неверный токен подписи'}, status=400)
        try:
            cancel_batch(batch=batch, user=request.user, reason=request.data.get('reason', ''))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'detail': 'Партия отменена'})

class ExtendTokenView(APIView):
    permission_classes = [IsEducator]

    def post(self, request, pk):
        batch = get_object_or_404(WasteBatch, pk=pk, creator_org=request.user.organization)
        serializer = ExtendTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not SignatureCheckMixin.check(request.user, serializer.validated_data['signature_token']):
            return Response({'detail': 'Неверный токен подписи'}, status=400)
        token = extend_batch_token(batch=batch, expires_at=serializer.validated_data['expires_at'])
        return Response({'expires_at': token.expires_at})

class BatchTimelineView(generics.ListAPIView):
    serializer_class = BatchStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        batch = get_object_or_404(WasteBatch, pk=self.kwargs['pk'])
        user = self.request.user
        allowed = user.is_superuser or user.user_roles.filter(role__in=['INSPECTOR', 'ADMIN']).exists() or batch.creator_org_id == user.organization_id or batch.processor_org_id == user.organization_id or has_driver_access_to_batch(user, batch)
        if not allowed:
            return batch.status_history.none()
        return batch.status_history.select_related('changed_by')

class BatchBlockedAttemptsView(generics.ListAPIView):
    serializer_class = BlockedAttemptSerializer
    permission_classes = [IsEducator]

    def get_queryset(self):
        batch = get_object_or_404(WasteBatch, pk=self.kwargs['pk'], creator_org=self.request.user.organization)
        return TokenAccessAttempt.objects.filter(batch=batch, success=False)

class ProcessorBatchListView(generics.ListAPIView):
    serializer_class = WasteBatchSerializer
    permission_classes = [IsProcessor]

    def get_queryset(self):
        return WasteBatch.objects.select_related('waste_type', 'creator_org', 'processor_org', 'current_driver', 'access_token').filter(processor_org=self.request.user.organization)

class ProcessorBatchDetailView(generics.RetrieveAPIView):
    serializer_class = WasteBatchSerializer
    permission_classes = [IsProcessor]

    def get_queryset(self):
        return WasteBatch.objects.select_related('waste_type', 'creator_org', 'processor_org', 'current_driver', 'access_token').filter(processor_org=self.request.user.organization)

class ProcessorAcceptBatchView(APIView):
    permission_classes = [IsProcessor]

    def post(self, request, pk):
        batch = get_object_or_404(WasteBatch, pk=pk, processor_org=request.user.organization)
        if not SignatureCheckMixin.check(request.user, request.data.get('signature_token', '')):
            return Response({'detail': 'Неверный токен подписи'}, status=400)
        try:
            accept_batch(batch=batch, user=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'detail': 'Партия принята'})

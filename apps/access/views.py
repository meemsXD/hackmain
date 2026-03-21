from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.users.serializers import SignatureCheckMixin
from apps.batches.models import WasteBatch
from apps.batches.serializers import WasteBatchSerializer
from apps.batches.services import pickup_batch, mark_delivered
from .models import DriverBatchAccessGrant
from .permissions import has_driver_access_to_batch
from .serializers import DriverAccessOpenSerializer, DriverListSerializer
from .services import open_driver_access

class DriverAccessOpenView(APIView):
    def post(self, request):
        serializer = DriverAccessOpenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            batch = open_driver_access(
                user=request.user,
                raw_token=serializer.validated_data.get('token'),
                manual_code=serializer.validated_data.get('manual_code'),
                ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
            )
        except PermissionError as exc:
            return Response({'detail': str(exc)}, status=403)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response(WasteBatchSerializer(batch).data)

class DriverActiveBatchListView(generics.ListAPIView):
    serializer_class = WasteBatchSerializer

    def get_queryset(self):
        batch_ids = DriverBatchAccessGrant.objects.filter(driver=self.request.user, expires_at__gt=timezone.now()).values_list('batch_id', flat=True)
        return WasteBatch.objects.select_related('waste_type', 'creator_org', 'processor_org', 'current_driver', 'access_token').filter(id__in=batch_ids)

class DriverBatchDetailView(generics.RetrieveAPIView):
    serializer_class = WasteBatchSerializer

    def get_queryset(self):
        batch_ids = DriverBatchAccessGrant.objects.filter(driver=self.request.user, expires_at__gt=timezone.now()).values_list('batch_id', flat=True)
        return WasteBatch.objects.select_related('waste_type', 'creator_org', 'processor_org', 'current_driver', 'access_token').filter(id__in=batch_ids)

class DriverPickupView(APIView):
    def post(self, request, pk):
        batch = get_object_or_404(WasteBatch, pk=pk)
        if not has_driver_access_to_batch(request.user, batch):
            return Response({'detail': 'Нет доступа к партии'}, status=403)
        if not SignatureCheckMixin.check(request.user, request.data.get('signature_token', '')):
            return Response({'detail': 'Неверный токен подписи'}, status=400)
        try:
            pickup_batch(batch=batch, user=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'detail': 'Забор подтвержден'})

class DriverMarkDeliveredView(APIView):
    def post(self, request, pk):
        batch = get_object_or_404(WasteBatch, pk=pk)
        if not has_driver_access_to_batch(request.user, batch):
            return Response({'detail': 'Нет доступа к партии'}, status=403)
        if not SignatureCheckMixin.check(request.user, request.data.get('signature_token', '')):
            return Response({'detail': 'Неверный токен подписи'}, status=400)
        try:
            mark_delivered(batch=batch, user=request.user)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=400)
        return Response({'detail': 'Доставка отмечена'})

class ProcessorDriverListView(generics.ListAPIView):
    serializer_class = DriverListSerializer

    def get_queryset(self):
        return self.request.user.organization.users.filter(user_roles__role='DRIVER').select_related('driver_profile').distinct()

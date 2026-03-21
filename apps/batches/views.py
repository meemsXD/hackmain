from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.audit.models import log
from .models import WasteBatch, BatchStatus, QRToken
from .serializers import WasteBatchSerializer, WasteBatchCreateSerializer, BatchStatusUpdateSerializer, QRTokenSerializer


class WasteBatchListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        return WasteBatchCreateSerializer if self.request.method == 'POST' else WasteBatchSerializer

    def get_queryset(self):
        return WasteBatch.objects.select_related('educator', 'qr_token').prefetch_related('statuses').all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        batch = serializer.save()
        return Response(WasteBatchSerializer(batch).data, status=status.HTTP_201_CREATED)


class WasteBatchDetailView(generics.RetrieveAPIView):
    serializer_class = WasteBatchSerializer
    queryset = WasteBatch.objects.select_related('educator', 'qr_token').prefetch_related('statuses')


class BatchStatusUpdateView(APIView):
    def post(self, request, pk):
        batch = get_object_or_404(WasteBatch, pk=pk)
        serializer = BatchStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']
        BatchStatus.objects.create(batch=batch, status=new_status)
        log(request.user, 'status_changed', 'waste_batch', str(batch.id), after={'status': new_status})
        return Response({'detail': f'Статус изменён на {new_status}'})


class QRTokenDetailView(generics.RetrieveAPIView):
    serializer_class = QRTokenSerializer

    def get_object(self):
        return get_object_or_404(QRToken, batch_id=self.kwargs['pk'])

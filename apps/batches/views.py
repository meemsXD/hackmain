from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Waste, Status, QR
from .serializers import WasteSerializer, WasteCreateSerializer, StatusUpdateSerializer, QRSerializer


class WasteListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        return WasteCreateSerializer if self.request.method == 'POST' else WasteSerializer

    def get_queryset(self):
        return Waste.objects.select_related('educator', 'qr').prefetch_related('statuses').all()

    def create(self, request, *args, **kwargs):
        serializer = WasteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        waste = serializer.save()
        return Response(WasteSerializer(waste).data, status=status.HTTP_201_CREATED)


class WasteDetailView(generics.RetrieveAPIView):
    serializer_class = WasteSerializer
    queryset         = Waste.objects.select_related('educator', 'qr').prefetch_related('statuses')


class StatusUpdateView(APIView):
    def post(self, request, pk):
        waste      = get_object_or_404(Waste, pk=pk)
        serializer = StatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Status.objects.create(waste=waste, state=serializer.validated_data['state'])
        return Response({'state': serializer.validated_data['state']})


class QRDetailView(generics.RetrieveAPIView):
    serializer_class = QRSerializer

    def get_object(self):
        return get_object_or_404(QR, waste_id=self.kwargs['pk'])

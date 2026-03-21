from django.urls import path
from .views import WasteBatchListCreateView, WasteBatchDetailView, BatchStatusUpdateView, QRTokenDetailView

urlpatterns = [
    path('', WasteBatchListCreateView.as_view(), name='batch-list'),
    path('<uuid:pk>/', WasteBatchDetailView.as_view(), name='batch-detail'),
    path('<uuid:pk>/status/', BatchStatusUpdateView.as_view(), name='batch-status'),
    path('<uuid:pk>/qr/', QRTokenDetailView.as_view(), name='batch-qr'),
]

from django.urls import path
from .views import (
    WasteListCreateView,
    WasteDetailView,
    StatusUpdateView,
    QRDetailView,
    QRScanView,
    QRScanLogListView,
    QRExtendView,
)

urlpatterns = [
    path('',                     WasteListCreateView.as_view(), name='waste-list'),
    path('qr/scan/',             QRScanView.as_view(),          name='qr-scan'),
    path('<str:pk>/',            WasteDetailView.as_view(),     name='waste-detail'),
    path('<str:pk>/status/',     StatusUpdateView.as_view(),    name='waste-status'),
    path('<str:pk>/qr/',         QRDetailView.as_view(),        name='waste-qr'),
    path('<str:pk>/qr/logs/',    QRScanLogListView.as_view(),   name='waste-qr-logs'),
    path('<str:pk>/qr/extend/',  QRExtendView.as_view(),        name='waste-qr-extend'),
]

from django.urls import path
from .views import WasteListCreateView, WasteDetailView, StatusUpdateView, QRDetailView

urlpatterns = [
    path('',                  WasteListCreateView.as_view(), name='waste-list'),
    path('<uuid:pk>/',        WasteDetailView.as_view(),     name='waste-detail'),
    path('<uuid:pk>/status/', StatusUpdateView.as_view(),    name='waste-status'),
    path('<uuid:pk>/qr/',     QRDetailView.as_view(),        name='waste-qr'),
]

from django.urls import path
from .views import DriverAccessOpenView, DriverActiveBatchListView, DriverBatchDetailView, DriverPickupView, DriverMarkDeliveredView

urlpatterns = [
    path('access/open', DriverAccessOpenView.as_view(), name='driver-access-open'),
    path('access/active', DriverActiveBatchListView.as_view(), name='driver-active-batches'),
    path('batches/<uuid:pk>', DriverBatchDetailView.as_view(), name='driver-batch-detail'),
    path('batches/<uuid:pk>/pickup', DriverPickupView.as_view(), name='driver-batch-pickup'),
    path('batches/<uuid:pk>/mark-delivered', DriverMarkDeliveredView.as_view(), name='driver-batch-delivered'),
]

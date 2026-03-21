from django.urls import path
from .views import ProcessorBatchListView, ProcessorBatchDetailView, ProcessorAcceptBatchView
from apps.access.views import ProcessorDriverListView

urlpatterns = [
    path('batches', ProcessorBatchListView.as_view(), name='processor-batch-list'),
    path('batches/<uuid:pk>', ProcessorBatchDetailView.as_view(), name='processor-batch-detail'),
    path('batches/<uuid:pk>/accept', ProcessorAcceptBatchView.as_view(), name='processor-batch-accept'),
    path('drivers', ProcessorDriverListView.as_view(), name='processor-drivers'),
]

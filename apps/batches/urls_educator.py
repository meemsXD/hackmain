from django.urls import path
from .views import EducatorBatchListCreateView, EducatorBatchDetailView, CancelBatchView, ExtendTokenView, BatchTimelineView, BatchBlockedAttemptsView

urlpatterns = [
    path('batches', EducatorBatchListCreateView.as_view(), name='educator-batch-list-create'),
    path('batches/<uuid:pk>', EducatorBatchDetailView.as_view(), name='educator-batch-detail'),
    path('batches/<uuid:pk>/cancel', CancelBatchView.as_view(), name='educator-batch-cancel'),
    path('batches/<uuid:pk>/token/extend', ExtendTokenView.as_view(), name='educator-batch-token-extend'),
    path('batches/<uuid:pk>/timeline', BatchTimelineView.as_view(), name='batch-timeline'),
    path('batches/<uuid:pk>/blocked-attempts', BatchBlockedAttemptsView.as_view(), name='batch-blocked-attempts'),
]

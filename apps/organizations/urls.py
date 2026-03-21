from django.urls import path
from .views import OrganizationListCreateView, OrganizationDetailView, EducatorProfileListView, ProcessorProfileListView

urlpatterns = [
    path('', OrganizationListCreateView.as_view(), name='org-list'),
    path('<uuid:pk>/', OrganizationDetailView.as_view(), name='org-detail'),
    path('educators/', EducatorProfileListView.as_view(), name='educator-list'),
    path('processors/', ProcessorProfileListView.as_view(), name='processor-list'),
]

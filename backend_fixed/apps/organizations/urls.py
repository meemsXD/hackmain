from django.urls import path
from .views import OrganizationSearchView

urlpatterns = [
    path('search', OrganizationSearchView.as_view(), name='organization-search'),
]

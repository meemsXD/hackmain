from django.urls import path
from .views import MyRoleRequestListCreateView, AdminRoleRequestListView, ApproveRoleRequestView, RejectRoleRequestView

urlpatterns = [
    path('my', MyRoleRequestListCreateView.as_view(), name='role-request-my'),
    path('', MyRoleRequestListCreateView.as_view(), name='role-request-create'),
    path('admin/list', AdminRoleRequestListView.as_view(), name='role-request-admin-list'),
    path('admin/<uuid:pk>/approve', ApproveRoleRequestView.as_view(), name='role-request-approve'),
    path('admin/<uuid:pk>/reject', RejectRoleRequestView.as_view(), name='role-request-reject'),
]

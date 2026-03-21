from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import RoleRequest
from .serializers import RoleRequestSerializer, AdminRoleRequestSerializer
from .permissions import IsAdminRole
from .services import approve_role_request, reject_role_request
from apps.audits.services import audit_log

class MyRoleRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = RoleRequestSerializer

    def get_queryset(self):
        return RoleRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        role_request = serializer.save(user=self.request.user, organization=self.request.user.organization)
        audit_log(self.request.user, 'role_request_created', 'role_request', str(role_request.id), None, {'role': role_request.role})

class AdminRoleRequestListView(generics.ListAPIView):
    serializer_class = AdminRoleRequestSerializer
    permission_classes = [IsAdminRole]
    queryset = RoleRequest.objects.select_related('user', 'organization').all()

class ApproveRoleRequestView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        rr = get_object_or_404(RoleRequest, pk=pk)
        approve_role_request(rr, request.user)
        return Response({'detail': 'Заявка одобрена'})

class RejectRoleRequestView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        rr = get_object_or_404(RoleRequest, pk=pk)
        reason = request.data.get('reason', '')
        reject_role_request(rr, request.user, reason)
        return Response({'detail': 'Заявка отклонена'})

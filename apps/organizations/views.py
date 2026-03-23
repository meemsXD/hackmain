from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in {'ADMIN', 'INSPECTOR'} or user.is_superuser:
            return Organization.objects.all().order_by('name')

        if not user.organization_id:
            return Organization.objects.none()

        return Organization.objects.filter(pk=user.organization_id)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'ADMIN' and not user.is_superuser:
            raise PermissionDenied('Only admin can create organizations.')
        serializer.save()


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in {'ADMIN', 'INSPECTOR'} or user.is_superuser:
            return Organization.objects.all()

        if not user.organization_id:
            return Organization.objects.none()

        return Organization.objects.filter(pk=user.organization_id)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role != 'ADMIN' and not user.is_superuser:
            raise PermissionDenied('Only admin can update organizations.')
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != 'ADMIN' and not user.is_superuser:
            raise PermissionDenied('Only admin can delete organizations.')
        instance.delete()

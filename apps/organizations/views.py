from rest_framework import generics, permissions
from .models import Organization, EducatorProfile, ProcessorProfile
from .serializers import OrganizationSerializer, EducatorProfileSerializer, ProcessorProfileSerializer


class OrganizationListCreateView(generics.ListCreateAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class OrganizationDetailView(generics.RetrieveAPIView):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()
    permission_classes = [permissions.AllowAny]


class EducatorProfileListView(generics.ListAPIView):
    serializer_class = EducatorProfileSerializer
    queryset = EducatorProfile.objects.select_related('organization')


class ProcessorProfileListView(generics.ListAPIView):
    serializer_class = ProcessorProfileSerializer
    queryset = ProcessorProfile.objects.select_related('organization').prefetch_related('drivers')

from rest_framework import generics
from .models import Organization
from .serializers import OrganizationSerializer


class OrganizationListCreateView(generics.ListCreateAPIView):
    queryset         = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset         = Organization.objects.all()
    serializer_class = OrganizationSerializer

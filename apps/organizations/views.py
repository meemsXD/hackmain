from rest_framework import generics, permissions
from .models import Organization
from .serializers import OrganizationSearchSerializer

class OrganizationSearchView(generics.ListAPIView):
    serializer_class = OrganizationSearchSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'inn', 'kpp']

    def get_queryset(self):
        qs = Organization.objects.all().order_by('name')
        q = self.request.query_params.get('q')
        if q:
            from django.db.models import Q
            qs = qs.filter(Q(name__icontains=q) | Q(inn__icontains=q) | Q(kpp__icontains=q))
        return qs.distinct()

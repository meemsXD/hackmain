from rest_framework import viewsets, permissions
from .models import WasteType
from .serializers import WasteTypeSerializer
from apps.roles.permissions import IsAdminRole

class WasteTypeViewSet(viewsets.ModelViewSet):
    queryset = WasteType.objects.all()
    serializer_class = WasteTypeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

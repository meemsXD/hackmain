from rest_framework import generics
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    queryset = AuditLog.objects.select_related('user').all()

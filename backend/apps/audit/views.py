from rest_framework import generics, permissions

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = AuditLog.objects.select_related('user').all()

        if user.role in {'ADMIN', 'INSPECTOR'} or user.is_superuser:
            return queryset

        return queryset.filter(user=user)

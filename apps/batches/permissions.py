from rest_framework.permissions import BasePermission

class HasRolePermission(BasePermission):
    required_role = None
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_roles.filter(role=self.required_role).exists()

class IsEducator(HasRolePermission):
    required_role = 'EDUCATOR'

class IsProcessor(HasRolePermission):
    required_role = 'PROCESSOR'

class IsInspectorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.user_roles.filter(role__in=['INSPECTOR', 'ADMIN']).exists()
        )

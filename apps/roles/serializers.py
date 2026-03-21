from rest_framework import serializers
from apps.common.enums import RoleChoices, RequestStatusChoices
from .models import RoleRequest, UserRole

class RoleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleRequest
        fields = ['id', 'role', 'status', 'payload', 'comment', 'rejection_reason', 'created_at', 'reviewed_at']
        read_only_fields = ['status', 'rejection_reason', 'created_at', 'reviewed_at']

    def validate_role(self, value):
        user = self.context['request'].user
        if user.user_roles.filter(role=value).exists():
            raise serializers.ValidationError('Роль уже выдана')
        if user.role_requests.filter(role=value, status=RequestStatusChoices.PENDING).exists():
            raise serializers.ValidationError('Заявка на эту роль уже подана')
        if value in [RoleChoices.ADMIN, RoleChoices.INSPECTOR]:
            raise serializers.ValidationError('Эта роль не выдается через публичную заявку')
        return value

class AdminRoleRequestSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = RoleRequest
        fields = ['id', 'user_email', 'organization_name', 'role', 'status', 'payload', 'comment', 'rejection_reason', 'created_at']

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'role', 'granted_at']

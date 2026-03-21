from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, DriverProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'organization', 'is_active', 'created_at']


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(choices=['EDUCATOR', 'DRIVER', 'PROCESSOR', 'INSPECTOR', 'ADMIN'])
    organization = serializers.UUIDField(required=False)
    vehicle_number = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({'email': 'Пользователь с таким email уже существует'})
        if attrs['role'] == 'DRIVER' and not attrs.get('vehicle_number'):
            raise serializers.ValidationError({'vehicle_number': 'Обязательное поле для водителя'})
        return attrs

    def create(self, validated_data):
        from apps.organizations.models import Organization
        org = None
        if validated_data.get('organization'):
            org = Organization.objects.get(id=validated_data['organization'])
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            role=validated_data['role'],
            organization=org,
        )
        if validated_data['role'] == 'DRIVER' and validated_data.get('vehicle_number'):
            DriverProfile.objects.create(user=user, vehicle_number=validated_data['vehicle_number'])
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

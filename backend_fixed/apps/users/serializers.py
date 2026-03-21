from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.common.enums import RoleChoices
from apps.organizations.models import Organization, EducatorOrgProfile, ProcessorOrgProfile
from apps.roles.models import RoleRequest, UserRole
from .models import User, DriverProfile
from django.contrib.auth.hashers import make_password, check_password

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['role', 'granted_at']

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    pending_roles = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    signature_configured = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'organization', 'roles', 'pending_roles', 'signature_configured']

    def get_roles(self, obj):
        return list(obj.user_roles.values_list('role', flat=True))

    def get_pending_roles(self, obj):
        return list(obj.role_requests.filter(status='PENDING').values_list('role', flat=True))

    def get_organization(self, obj):
        if not obj.organization:
            return None
        return {'id': str(obj.organization.id), 'name': obj.organization.name, 'inn': obj.organization.inn, 'kpp': obj.organization.kpp, 'status': obj.organization.status}

    def get_signature_configured(self, obj):
        return bool(obj.signature_token_hash)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['roles'] = list(user.user_roles.values_list('role', flat=True))
        return token

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Неверный email или пароль')
        attrs['user'] = user
        return attrs

class RegisterSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    organization_mode = serializers.ChoiceField(choices=['create', 'join'])
    organization_id = serializers.UUIDField(required=False)
    organization_name = serializers.CharField(required=False)
    inn = serializers.CharField(required=False)
    kpp = serializers.CharField(required=False)
    legal_address = serializers.CharField(required=False)
    roles = serializers.ListField(child=serializers.ChoiceField(choices=[RoleChoices.EDUCATOR, RoleChoices.DRIVER, RoleChoices.PROCESSOR]), allow_empty=False)
    waste_license_number = serializers.CharField(required=False, allow_blank=True)
    default_pickup_address = serializers.CharField(required=False, allow_blank=True)
    recycling_license_number = serializers.CharField(required=False, allow_blank=True)
    facility_address = serializers.CharField(required=False, allow_blank=True)
    vehicle_number = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['organization_mode'] == 'create':
            required = ['organization_name', 'inn', 'kpp', 'legal_address']
            for field in required:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: 'Обязательное поле'})
        else:
            if not attrs.get('organization_id'):
                raise serializers.ValidationError({'organization_id': 'Обязательное поле'})
        if RoleChoices.EDUCATOR in attrs['roles']:
            for field in ['waste_license_number', 'default_pickup_address']:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: 'Обязательное поле'})
        if RoleChoices.PROCESSOR in attrs['roles']:
            for field in ['recycling_license_number', 'facility_address']:
                if not attrs.get(field):
                    raise serializers.ValidationError({field: 'Обязательное поле'})
        if RoleChoices.DRIVER in attrs['roles'] and not attrs.get('vehicle_number'):
            raise serializers.ValidationError({'vehicle_number': 'Обязательное поле'})
        return attrs

    def create(self, validated_data):
        organization = None
        if validated_data['organization_mode'] == 'create':
            organization = Organization.objects.create(
                name=validated_data['organization_name'],
                inn=validated_data['inn'],
                kpp=validated_data['kpp'],
                legal_address=validated_data['legal_address'],
            )
        else:
            organization = Organization.objects.get(id=validated_data['organization_id'])

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone=validated_data.get('phone', ''),
            organization=organization,
        )

        if RoleChoices.DRIVER in validated_data['roles']:
            DriverProfile.objects.create(user=user, vehicle_number=validated_data['vehicle_number'])

        for role in validated_data['roles']:
            RoleRequest.objects.create(
                user=user,
                organization=organization,
                role=role,
                payload={
                    'waste_license_number': validated_data.get('waste_license_number'),
                    'default_pickup_address': validated_data.get('default_pickup_address'),
                    'recycling_license_number': validated_data.get('recycling_license_number'),
                    'facility_address': validated_data.get('facility_address'),
                    'vehicle_number': validated_data.get('vehicle_number'),
                },
            )

        if RoleChoices.EDUCATOR in validated_data['roles'] and not hasattr(organization, 'educator_profile'):
            EducatorOrgProfile.objects.create(
                organization=organization,
                waste_license_number=validated_data['waste_license_number'],
                default_pickup_address=validated_data['default_pickup_address'],
            )
        if RoleChoices.PROCESSOR in validated_data['roles'] and not hasattr(organization, 'processor_profile'):
            ProcessorOrgProfile.objects.create(
                organization=organization,
                recycling_license_number=validated_data['recycling_license_number'],
                facility_address=validated_data['facility_address'],
            )
        return user

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['full_name', 'phone']

class SignatureSetupSerializer(serializers.Serializer):
    signature_token = serializers.CharField(write_only=True, min_length=4, max_length=128)

    def save(self, **kwargs):
        user = self.context['request'].user
        user.signature_token_hash = make_password(self.validated_data['signature_token'])
        user.save(update_fields=['signature_token_hash', 'updated_at'])
        return user

class SignatureCheckMixin:
    @staticmethod
    def check(user, raw_token):
        return bool(user.signature_token_hash and check_password(raw_token, user.signature_token_hash))

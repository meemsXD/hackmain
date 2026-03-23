from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import DriverProfile, MedicalOrganization, Recycler, User


class DriverProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    user_login = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()

    class Meta:
        model = DriverProfile
        fields = ['id', 'vehicle_number', 'user_id', 'user_login', 'user_full_name']

    @staticmethod
    def _safe_user(obj):
        try:
            return obj.user
        except User.DoesNotExist:
            return None

    def get_user_id(self, obj):
        user = self._safe_user(obj)
        return user.id if user else None

    def get_user_login(self, obj):
        user = self._safe_user(obj)
        return user.login if user else None

    def get_user_full_name(self, obj):
        user = self._safe_user(obj)
        return user.full_name if user else None


class MedicalOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalOrganization
        fields = ['id', 'license_number', 'address']


class RecyclerSerializer(serializers.ModelSerializer):
    drivers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Recycler
        fields = ['id', 'license_number', 'facility_address', 'drivers']


class RecyclerOptionSerializer(serializers.ModelSerializer):
    organization_id = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = Recycler
        fields = ['id', 'license_number', 'facility_address', 'organization_id', 'organization_name', 'user_id']

    @staticmethod
    def _safe_user(obj):
        try:
            return obj.user
        except User.DoesNotExist:
            return None

    def get_organization_id(self, obj):
        user = self._safe_user(obj)
        return user.organization_id if user else None

    def get_organization_name(self, obj):
        user = self._safe_user(obj)
        if not user or not user.organization:
            return None
        return user.organization.name

    def get_user_id(self, obj):
        user = self._safe_user(obj)
        return user.id if user else None


class UserSerializer(serializers.ModelSerializer):
    driver_profile = DriverProfileSerializer(read_only=True)
    educator_profile = MedicalOrganizationSerializer(source='medical_org', read_only=True)
    processor_profile = RecyclerSerializer(source='recycler_profile', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'login',
            'full_name',
            'role',
            'organization',
            'driver_profile',
            'educator_profile',
            'processor_profile',
        ]


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    vehicle_number = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    facility_address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'login',
            'full_name',
            'role',
            'organization',
            'password',
            'vehicle_number',
            'license_number',
            'address',
            'facility_address',
        ]

    def validate(self, attrs):
        role = attrs.get('role')
        vehicle_number = (attrs.get('vehicle_number') or '').strip()
        license_number = (attrs.get('license_number') or '').strip()
        address = (attrs.get('address') or '').strip()
        facility_address = (attrs.get('facility_address') or '').strip()

        if role == 'DRIVER' and not vehicle_number:
            raise serializers.ValidationError({'vehicle_number': 'Укажите номер ТС.'})

        if role == 'RECYCLER':
            if not license_number:
                raise serializers.ValidationError({'license_number': 'Укажите номер лицензии.'})
            if not address:
                raise serializers.ValidationError({'address': 'Укажите адрес организации.'})

        if role == 'MEDICAL':
            if not license_number:
                raise serializers.ValidationError({'license_number': 'Укажите номер лицензии.'})
            if not facility_address:
                raise serializers.ValidationError({'facility_address': 'Укажите адрес площадки.'})

        return attrs

    def create(self, validated_data):
        vehicle_number = (validated_data.pop('vehicle_number', '') or '').strip()
        license_number = (validated_data.pop('license_number', '') or '').strip()
        address = (validated_data.pop('address', '') or '').strip()
        facility_address = (validated_data.pop('facility_address', '') or '').strip()
        password = validated_data.pop('password')

        user = User(**validated_data)
        if user.role == 'ADMIN':
            user.is_staff = True
            user.is_superuser = True
        user.set_password(password)
        user.save()

        update_fields: list[str] = []
        if user.role == 'DRIVER':
            profile = DriverProfile.objects.create(vehicle_number=vehicle_number)
            user.driver_profile = profile
            update_fields.append('driver_profile')
        elif user.role == 'RECYCLER':
            profile = MedicalOrganization.objects.create(license_number=license_number, address=address)
            user.medical_org = profile
            update_fields.append('medical_org')
        elif user.role == 'MEDICAL':
            profile = Recycler.objects.create(license_number=license_number, facility_address=facility_address)
            user.recycler_profile = profile
            update_fields.append('recycler_profile')

        if update_fields:
            user.save(update_fields=update_fields)

        return user


class ProcessorDriverCreateSerializer(serializers.Serializer):
    vehicle_number = serializers.CharField(max_length=64)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    login = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(required=False, allow_blank=True, write_only=True)
    organization = serializers.IntegerField(required=False)

    def validate(self, attrs):
        full_name = (attrs.get('full_name') or '').strip()
        login = (attrs.get('login') or '').strip()
        password = (attrs.get('password') or '').strip()

        has_auth_payload = bool(full_name or login or password)
        if has_auth_payload and not (full_name and login and password):
            raise serializers.ValidationError(
                'Для создания учетной записи водителя укажите full_name, login и password полностью.'
            )

        attrs['full_name'] = full_name
        attrs['login'] = login
        attrs['password'] = password
        attrs['vehicle_number'] = attrs['vehicle_number'].strip()

        if not attrs['vehicle_number']:
            raise serializers.ValidationError({'vehicle_number': 'Укажите номер ТС.'})

        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login'

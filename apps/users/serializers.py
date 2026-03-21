from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, DriverProfile, MedicalOrganization, Recycler


class DriverProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DriverProfile
        fields = ['id', 'vehicle_number']


class MedicalOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MedicalOrganization
        fields = ['id', 'license_number', 'address']


class RecyclerSerializer(serializers.ModelSerializer):
    drivers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model  = Recycler
        fields = ['id', 'license_number', 'facility_address', 'drivers']


class UserSerializer(serializers.ModelSerializer):
    driver_profile    = DriverProfileSerializer(read_only=True)
    educator_profile  = MedicalOrganizationSerializer(read_only=True)
    processor_profile = RecyclerSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'login', 'full_name', 'role', 'organization',
                  'driver_profile', 'educator_profile', 'processor_profile']


class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True)
    vehicle_number   = serializers.CharField(required=False)
    license_number   = serializers.CharField(required=False)
    address          = serializers.CharField(required=False)
    facility_address = serializers.CharField(required=False)

    class Meta:
        model  = User
        fields = ['login', 'full_name', 'role', 'organization', 'password',
                  'vehicle_number', 'license_number', 'address', 'facility_address']

    def create(self, validated_data):
        vehicle_number   = validated_data.pop('vehicle_number', None)
        license_number   = validated_data.pop('license_number', None)
        address          = validated_data.pop('address', None)
        facility_address = validated_data.pop('facility_address', None)
        password         = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == 'DRIVER' and vehicle_number:
            DriverProfile.objects.create(user=user, vehicle_number=vehicle_number)
        elif user.role == 'EDUCATOR' and license_number:
            MedicalOrganization.objects.create(user=user, license_number=license_number, address=address or '')
        elif user.role == 'PROCESSOR' and license_number:
            Recycler.objects.create(user=user, license_number=license_number, facility_address=facility_address or '')

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'login'

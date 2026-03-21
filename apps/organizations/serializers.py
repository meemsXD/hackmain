from rest_framework import serializers
from .models import Organization, EducatorProfile, ProcessorProfile


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'inn', 'kpp', 'created_at']


class EducatorProfileSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    class Meta:
        model = EducatorProfile
        fields = ['id', 'organization', 'license_number', 'pickup_address']


class ProcessorProfileSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    class Meta:
        model = ProcessorProfile
        fields = ['id', 'organization', 'license_number', 'facility_address', 'drivers']

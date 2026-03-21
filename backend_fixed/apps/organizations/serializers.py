from rest_framework import serializers
from .models import Organization, EducatorOrgProfile, ProcessorOrgProfile

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'inn', 'kpp', 'legal_address', 'status']

class OrganizationSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'inn', 'kpp', 'status']

class EducatorOrgProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducatorOrgProfile
        fields = ['waste_license_number', 'default_pickup_address']

class ProcessorOrgProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessorOrgProfile
        fields = ['recycling_license_number', 'facility_address']

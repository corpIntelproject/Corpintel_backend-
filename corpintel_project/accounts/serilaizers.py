from rest_framework import serializers
from .models import CorpTenant, CorpUser

from rest_framework import serializers
from .models import CorpTenant, CorpUser

class CompanyRegistrationSerializer(serializers.Serializer):
    # ALL fields are now strictly required by default!
    company_name = serializers.CharField(max_length=255)
    registration_number = serializers.CharField(max_length=100)
    company_website = serializers.URLField()
    headquarters_location = serializers.CharField(max_length=255)
    industry_type = serializers.CharField(max_length=150)
    
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_name = serializers.CharField(max_length=150)

    def create(self, validated_data):
        # 1. Create the Company Profile
        tenant = CorpTenant.objects.create(
            organization_name=validated_data['company_name'],
            registration_number=validated_data['registration_number'],
            company_website=validated_data['company_website'],
            headquarters_location=validated_data['headquarters_location'],
            industry_type=validated_data['industry_type']
        )
        
        # 2. Create the Company Admin
        user = CorpUser.objects.create_user(
            username=validated_data['admin_email'],
            email=validated_data['admin_email'],
            password=validated_data['admin_password'],
            first_name=validated_data['admin_name'],
            tenant_profile=tenant,
            system_role=CorpUser.AccessRoles.COMPANY_ADMIN
        )
        return user
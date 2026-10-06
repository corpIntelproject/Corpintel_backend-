import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class CorpTenant(models.Model):
    """The main Company table for the system."""
    tenant_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_name = models.CharField(max_length=255, unique=True)
    
    # --- Company Identity & Verification ---
    registration_number = models.CharField(max_length=100, blank=True, null=True, help_text="CIN, GSTIN, or Tax ID")
    company_website = models.URLField(max_length=255, blank=True, null=True)
    
    # --- New: Location & Operations ---
    headquarters_location = models.CharField(max_length=255, blank=True, null=True, help_text="City, State, or Country")
    industry_type = models.CharField(max_length=150, blank=True, null=True, help_text="e.g., Healthcare, Finance, IT")
    employee_count_estimate = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 1-50, 51-200")
    
    registered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization_name} ({self.headquarters_location})"

class CorpUser(AbstractUser):
    user_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_profile = models.ForeignKey(CorpTenant, on_delete=models.CASCADE, related_name='tenant_users', null=True, blank=True)
    
    class AccessRoles(models.TextChoices):
        COMPANY_ADMIN = 'CORP_ADMIN', 'Corporate Administrator'
        EMPLOYEE = 'CORP_EMPLOYEE', 'Standard Employee'
        
    system_role = models.CharField(max_length=20, choices=AccessRoles.choices, default=AccessRoles.EMPLOYEE)
    
    # --- OTP VERIFICATION FIELDS ---
    is_email_verified = models.BooleanField(default=False)
    email_otp = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.username} | Role: {self.system_role}"

from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.contrib.auth.models import User


class Tenant(TenantMixin):
    """
    Tenant model for multi-tenant SaaS architecture
    """
    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    # Company Information
    company_name = models.CharField(max_length=200)
    company_description = models.TextField(blank=True)
    company_logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    company_website = models.URLField(blank=True)
    
    # Contact Information
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Subscription Information
    subscription_plan = models.CharField(max_length=50, default='basic')
    subscription_status = models.CharField(max_length=20, default='active')
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    
    # Settings
    is_active = models.BooleanField(default=True)
    max_users = models.IntegerField(default=5)
    max_storage_gb = models.IntegerField(default=10)
    max_monthly_uploads = models.IntegerField(default=100)
    
    # Features
    ai_insights_enabled = models.BooleanField(default=True)
    advanced_analytics_enabled = models.BooleanField(default=False)
    custom_branding_enabled = models.BooleanField(default=False)
    api_access_enabled = models.BooleanField(default=False)
    
    auto_create_schema = True
    auto_drop_schema = True
    
    class Meta:
        db_table = 'tenants_tenant'
    
    def __str__(self):
        return self.name


class Domain(DomainMixin):
    """
    Domain model for tenant routing
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    
    class Meta:
        db_table = 'tenants_domain'
    
    def __str__(self):
        return f"{self.domain} -> {self.tenant.name}"


class TenantUser(models.Model):
    """
    Extended user model for tenant-specific information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='tenant_users')
    
    # User Role
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('analyst', 'Business Analyst'),
        ('viewer', 'Viewer'),
        ('guest', 'Guest'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='analyst')
    
    # Profile Information
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='user_profiles/', blank=True, null=True)
    
    # Permissions
    can_upload_data = models.BooleanField(default=True)
    can_create_reports = models.BooleanField(default=True)
    can_view_all_data = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'tenant']
        db_table = 'tenants_tenantuser'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.tenant.name}"
    
    @property
    def is_owner(self):
        return self.role == 'owner'
    
    @property
    def is_admin(self):
        return self.role in ['owner', 'admin']
    
    @property
    def can_manage_tenant(self):
        return self.role in ['owner', 'admin'] and self.can_manage_settings

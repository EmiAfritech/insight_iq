from django.contrib import admin
from django_tenants.admin import TenantAdminMixin
from .models import Tenant, Domain, TenantUser


@admin.register(Tenant)
class TenantAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'company_name', 'subscription_plan', 'is_active', 'created_on']
    list_filter = ['subscription_plan', 'is_active', 'created_on']
    search_fields = ['name', 'company_name', 'contact_email']
    readonly_fields = ['created_on', 'updated_on']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company_name', 'company_description', 'company_logo', 'company_website')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code')
        }),
        ('Subscription', {
            'fields': ('subscription_plan', 'subscription_status', 'subscription_start_date', 'subscription_end_date')
        }),
        ('Settings', {
            'fields': ('is_active', 'max_users', 'max_storage_gb', 'max_monthly_uploads')
        }),
        ('Features', {
            'fields': ('ai_insights_enabled', 'advanced_analytics_enabled', 'custom_branding_enabled', 'api_access_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_on', 'updated_on')
        }),
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary']
    list_filter = ['is_primary']
    search_fields = ['domain', 'tenant__name']


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'tenant__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'tenant', 'role')
        }),
        ('Profile', {
            'fields': ('phone', 'department', 'job_title', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('can_upload_data', 'can_create_reports', 'can_view_all_data', 'can_manage_users', 'can_manage_settings')
        }),
        ('Status', {
            'fields': ('is_active', 'last_login')
        }),
    )

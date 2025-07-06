from django.contrib import admin
from .models import ContactMessage, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "Mark selected messages as read"
    
    actions = [mark_as_read]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_description', 'site_logo')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'support_email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'github_url')
        }),
        ('Analytics', {
            'fields': ('google_analytics_id', 'facebook_pixel_id')
        }),
        ('Features', {
            'fields': ('maintenance_mode', 'allow_registration')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False

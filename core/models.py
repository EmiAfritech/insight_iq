from django.db import models
from django.contrib.auth.models import User


class ContactMessage(models.Model):
    """
    Model for storing contact form messages
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'core_contactmessage'
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class SiteSettings(models.Model):
    """
    Model for storing site-wide settings
    """
    site_name = models.CharField(max_length=100, default='InsightIQ')
    site_description = models.TextField(blank=True)
    site_logo = models.ImageField(upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField(default='contact@insightiq.com')
    support_email = models.EmailField(default='support@insightiq.com')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=50, blank=True)
    facebook_pixel_id = models.CharField(max_length=50, blank=True)
    
    # Features
    maintenance_mode = models.BooleanField(default=False)
    allow_registration = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
        db_table = 'core_sitesettings'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            self.pk = SiteSettings.objects.first().pk
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create site settings"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'InsightIQ',
                'site_description': 'AI-Powered Business Analytics Platform',
                'contact_email': 'contact@insightiq.com',
                'support_email': 'support@insightiq.com',
            }
        )
        return settings

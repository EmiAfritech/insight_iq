from django.db import models
from django.contrib.auth.models import User
from tenants.models import Tenant
import uuid


class SubscriptionPlan(models.Model):
    """
    Model for subscription plans
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    billing_period = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime'),
    ])
    
    # Features
    max_users = models.IntegerField()
    max_storage_gb = models.IntegerField()
    max_monthly_uploads = models.IntegerField()
    ai_insights_enabled = models.BooleanField(default=True)
    advanced_analytics_enabled = models.BooleanField(default=False)
    custom_branding_enabled = models.BooleanField(default=False)
    api_access_enabled = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    
    # Stripe integration
    stripe_price_id = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
        db_table = 'subscriptions_subscriptionplan'
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.billing_period}"


class Subscription(models.Model):
    """
    Model for tenant subscriptions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    
    # Subscription details
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
        ('suspended', 'Suspended'),
        ('trial', 'Trial'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    
    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Stripe integration
    stripe_subscription_id = models.CharField(max_length=100, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    
    # Usage tracking
    current_users = models.IntegerField(default=0)
    current_storage_gb = models.FloatField(default=0)
    current_monthly_uploads = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subscriptions_subscription'
    
    def __str__(self):
        return f"{self.tenant.name} - {self.plan.name}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_trial(self):
        return self.status == 'trial'
    
    @property
    def days_remaining(self):
        from django.utils import timezone
        if self.end_date:
            return (self.end_date - timezone.now()).days
        return 0


class SubscriptionUsage(models.Model):
    """
    Model for tracking subscription usage
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usage_records')
    
    # Usage metrics
    users_count = models.IntegerField(default=0)
    storage_gb = models.FloatField(default=0)
    monthly_uploads = models.IntegerField(default=0)
    api_calls = models.IntegerField(default=0)
    
    # Period
    usage_date = models.DateField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['subscription', 'usage_date']
        db_table = 'subscriptions_subscriptionusage'
    
    def __str__(self):
        return f"{self.subscription.tenant.name} - {self.usage_date}"

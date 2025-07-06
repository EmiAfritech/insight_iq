from django.db import models
from django.contrib.auth.models import User
from analytics.models import DataSet, Analysis, Chart
import uuid


class Dashboard(models.Model):
    """
    Model for custom dashboards
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Dashboard configuration
    layout = models.JSONField(default=dict)
    theme = models.CharField(max_length=50, default='default')
    
    # Settings
    is_public = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    auto_refresh = models.BooleanField(default=False)
    refresh_interval = models.IntegerField(default=300)  # seconds
    
    # Access control
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_dashboards')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_viewed = models.DateTimeField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-updated_at']
        db_table = 'dashboards_dashboard'
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """
    Model for dashboard widgets
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    
    # Widget content
    title = models.CharField(max_length=200)
    
    # Widget types
    WIDGET_TYPES = [
        ('chart', 'Chart'),
        ('metric', 'Metric'),
        ('table', 'Table'),
        ('text', 'Text'),
        ('image', 'Image'),
        ('iframe', 'IFrame'),
        ('custom', 'Custom'),
    ]
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    
    # Widget data source
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE, null=True, blank=True)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, null=True, blank=True)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, null=True, blank=True)
    
    # Widget configuration
    configuration = models.JSONField(default=dict)
    custom_data = models.JSONField(default=dict)
    
    # Layout
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    
    # Settings
    is_visible = models.BooleanField(default=True)
    auto_refresh = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        db_table = 'dashboards_dashboardwidget'
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class DashboardTemplate(models.Model):
    """
    Model for pre-built dashboard templates
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Template categories
    CATEGORIES = [
        ('executive', 'Executive Summary'),
        ('sales', 'Sales Analytics'),
        ('marketing', 'Marketing Analytics'),
        ('finance', 'Financial Analytics'),
        ('operations', 'Operations Analytics'),
        ('hr', 'HR Analytics'),
        ('customer', 'Customer Analytics'),
        ('general', 'General Analytics'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    # Template configuration
    layout_template = models.JSONField(default=dict)
    widgets_template = models.JSONField(default=list)
    
    # Template metadata
    is_system_template = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    # Preview
    preview_image = models.ImageField(upload_to='dashboard_templates/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
        db_table = 'dashboards_dashboardtemplate'
    
    def __str__(self):
        return self.name


class DashboardShare(models.Model):
    """
    Model for dashboard sharing
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_dashboards_created')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_dashboards_received')
    
    # Permission levels
    PERMISSION_LEVELS = [
        ('view', 'View Only'),
        ('edit', 'Edit'),
        ('admin', 'Admin'),
    ]
    permission_level = models.CharField(max_length=10, choices=PERMISSION_LEVELS, default='view')
    
    # Settings
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['dashboard', 'shared_with']
        db_table = 'dashboards_dashboardshare'
    
    def __str__(self):
        return f"{self.dashboard.name} shared with {self.shared_with.username}"


class DashboardView(models.Model):
    """
    Model for tracking dashboard views
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # View details
    viewed_at = models.DateTimeField(auto_now_add=True)
    session_duration = models.IntegerField(null=True, blank=True)  # seconds
    
    # User agent and IP for analytics
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'dashboards_dashboardview'
    
    def __str__(self):
        return f"{self.dashboard.name} viewed by {self.user.username}"

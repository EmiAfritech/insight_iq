from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
import uuid


class DataSource(models.Model):
    """
    Model for external data sources
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Data source type
    SOURCE_TYPES = [
        ('database', 'Database'),
        ('api', 'API'),
        ('file', 'File'),
        ('cloud', 'Cloud Storage'),
        ('erp', 'ERP System'),
        ('crm', 'CRM System'),
        ('other', 'Other'),
    ]
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    
    # Connection details
    connection_string = models.TextField(blank=True)
    host = models.CharField(max_length=255, blank=True)
    port = models.IntegerField(null=True, blank=True)
    database_name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)  # Should be encrypted
    
    # API details
    api_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=500, blank=True)
    api_headers = models.JSONField(default=dict)
    
    # File/Cloud details
    file_path = models.CharField(max_length=500, blank=True)
    access_token = models.CharField(max_length=500, blank=True)
    
    # Additional configuration
    configuration = models.JSONField(default=dict)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('testing', 'Testing'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    last_tested = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'data_sources_datasource'
    
    def __str__(self):
        return self.name


class DataSourceConnection(models.Model):
    """
    Model for tracking data source connections and usage
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='connections')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Connection details
    connected_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    # Data pulled
    total_records_pulled = models.BigIntegerField(default=0)
    last_pull_count = models.IntegerField(default=0)
    last_pull_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['data_source', 'user']
        db_table = 'data_sources_datasourceconnection'
    
    def __str__(self):
        return f"{self.user.username} - {self.data_source.name}"


class DataPull(models.Model):
    """
    Model for tracking data pulls from external sources
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='pulls')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Pull configuration
    query = models.TextField(blank=True)
    parameters = models.JSONField(default=dict)
    
    # Results
    records_count = models.IntegerField(default=0)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(default=0)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'data_sources_datapull'
    
    def __str__(self):
        return f"{self.data_source.name} - {self.created_at}"


class DataSourceTemplate(models.Model):
    """
    Model for pre-configured data source templates
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    source_type = models.CharField(max_length=20, choices=DataSource.SOURCE_TYPES)
    
    # Template configuration
    configuration_template = models.JSONField(default=dict)
    connection_template = models.JSONField(default=dict)
    
    # Common systems
    SYSTEM_TYPES = [
        ('mysql', 'MySQL'),
        ('postgresql', 'PostgreSQL'),
        ('mssql', 'Microsoft SQL Server'),
        ('oracle', 'Oracle'),
        ('sqlite', 'SQLite'),
        ('mongodb', 'MongoDB'),
        ('salesforce', 'Salesforce'),
        ('hubspot', 'HubSpot'),
        ('quickbooks', 'QuickBooks'),
        ('xero', 'Xero'),
        ('google_analytics', 'Google Analytics'),
        ('facebook_ads', 'Facebook Ads'),
        ('aws_s3', 'AWS S3'),
        ('google_sheets', 'Google Sheets'),
        ('custom', 'Custom'),
    ]
    system_type = models.CharField(max_length=30, choices=SYSTEM_TYPES, default='custom')
    
    # Template metadata
    is_system_template = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    
    # Documentation
    setup_instructions = models.TextField(blank=True)
    required_fields = models.JSONField(default=list)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
        db_table = 'data_sources_datasourcetemplate'
    
    def __str__(self):
        return self.name

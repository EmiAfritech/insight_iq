from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from tenants.models import Tenant
from dashboards.models import Dashboard
from analytics.models import Analysis
import uuid

User = get_user_model()


class ReportTemplate(models.Model):
    """Template for creating standardized reports"""
    TEMPLATE_TYPES = [
        ('financial', 'Financial Report'),
        ('sales', 'Sales Report'),
        ('marketing', 'Marketing Report'),
        ('operations', 'Operations Report'),
        ('custom', 'Custom Report'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    template_data = models.JSONField(default=dict, help_text="Template configuration and layout")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_report_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.tenant.name}"


class Report(models.Model):
    """Generated reports with data and visualizations"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('scheduled', 'Scheduled'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('powerpoint', 'PowerPoint'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Data sources
    dashboards = models.ManyToManyField(Dashboard, blank=True, related_name='reports')
    analyses = models.ManyToManyField(Analysis, blank=True, related_name='reports')
    
    # Report content
    content = models.JSONField(default=dict, help_text="Report content and structure")
    executive_summary = models.TextField(blank=True)
    key_insights = models.JSONField(default=list, help_text="List of key insights")
    recommendations = models.TextField(blank=True)
    
    # Generation settings
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='pdf')
    include_charts = models.BooleanField(default=True)
    include_data_tables = models.BooleanField(default=True)
    include_appendix = models.BooleanField(default=False)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    generated_at = models.DateTimeField(null=True, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ])
    next_generation = models.DateTimeField(null=True, blank=True)
    
    # Access and sharing
    is_public = models.BooleanField(default=False)
    share_token = models.CharField(max_length=100, blank=True, unique=True)
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.tenant.name}"
    
    def get_absolute_url(self):
        return reverse('reports:report_detail', kwargs={'report_id': self.id})
    
    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = str(uuid.uuid4())
        super().save(*args, **kwargs)


class ReportSection(models.Model):
    """Sections within a report"""
    SECTION_TYPES = [
        ('header', 'Header'),
        ('summary', 'Executive Summary'),
        ('chart', 'Chart/Visualization'),
        ('table', 'Data Table'),
        ('text', 'Text Content'),
        ('insights', 'Key Insights'),
        ('recommendations', 'Recommendations'),
        ('appendix', 'Appendix'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    content = models.JSONField(default=dict, help_text="Section content and configuration")
    order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.title} - {self.report.title}"


class ReportShare(models.Model):
    """Shared report access tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_reports')
    shared_with_email = models.EmailField()
    message = models.TextField(blank=True)
    access_level = models.CharField(max_length=20, choices=[
        ('view', 'View Only'),
        ('download', 'View & Download'),
    ], default='view')
    expires_at = models.DateTimeField(null=True, blank=True)
    accessed_at = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['report', 'shared_with_email']
        
    def __str__(self):
        return f"{self.report.title} shared with {self.shared_with_email}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ReportComment(models.Model):
    """Comments on reports for collaboration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_comments')
    content = models.TextField()
    section = models.ForeignKey(ReportSection, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Comment on {self.report.title} by {self.author.username}"


class ReportExport(models.Model):
    """Track report exports and downloads"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='exports')
    exported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_exports')
    format = models.CharField(max_length=20, choices=Report.FORMAT_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(null=True, blank=True)
    export_settings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.report.title} exported as {self.format}"

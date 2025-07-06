from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
import uuid


class DataSet(models.Model):
    """
    Model for storing uploaded datasets
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # File information
    file = models.FileField(
        upload_to='datasets/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls', 'json'])]
    )
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=10)
    
    # Data information
    total_rows = models.IntegerField(default=0)
    total_columns = models.IntegerField(default=0)
    columns_info = models.JSONField(default=dict)  # Store column names and types
    
    # Status
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    error_message = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_analyzed = models.DateTimeField(null=True, blank=True)
    
    # Analytics settings
    is_public = models.BooleanField(default=False)
    tags = models.JSONField(default=list)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'analytics_dataset'
    
    def __str__(self):
        return self.name
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)


class Analysis(models.Model):
    """
    Model for storing analysis results
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE, related_name='analyses')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Analysis type
    ANALYSIS_TYPES = [
        ('descriptive', 'Descriptive Statistics'),
        ('correlation', 'Correlation Analysis'),
        ('trend', 'Trend Analysis'),
        ('predictive', 'Predictive Analysis'),
        ('clustering', 'Clustering Analysis'),
        ('anomaly', 'Anomaly Detection'),
        ('custom', 'Custom Analysis'),
    ]
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    
    # Configuration
    configuration = models.JSONField(default=dict)
    selected_columns = models.JSONField(default=list)
    
    # Results
    results = models.JSONField(default=dict)
    charts = models.JSONField(default=list)
    insights = models.JSONField(default=list)
    
    # AI-generated content
    ai_summary = models.TextField(blank=True)
    ai_insights = models.JSONField(default=list)
    ai_recommendations = models.JSONField(default=list)
    
    # Status
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    error_message = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    execution_time = models.FloatField(null=True, blank=True)  # in seconds
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'analytics_analysis'
    
    def __str__(self):
        return f"{self.name} - {self.dataset.name}"


class Chart(models.Model):
    """
    Model for storing chart configurations and data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='chart_objects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Chart configuration
    CHART_TYPES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('scatter', 'Scatter Plot'),
        ('heatmap', 'Heatmap'),
        ('histogram', 'Histogram'),
        ('box', 'Box Plot'),
        ('area', 'Area Chart'),
        ('gauge', 'Gauge Chart'),
    ]
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    
    # Data and configuration
    data = models.JSONField(default=dict)
    configuration = models.JSONField(default=dict)
    
    # Display settings
    width = models.IntegerField(default=800)
    height = models.IntegerField(default=600)
    is_interactive = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'analytics_chart'
    
    def __str__(self):
        return f"{self.name} ({self.chart_type})"


class Insight(models.Model):
    """
    Model for storing AI-generated insights
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='insight_objects')
    
    # Insight content
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Insight type
    INSIGHT_TYPES = [
        ('trend', 'Trend Insight'),
        ('anomaly', 'Anomaly Detection'),
        ('correlation', 'Correlation Finding'),
        ('prediction', 'Prediction'),
        ('recommendation', 'Recommendation'),
        ('summary', 'Summary'),
    ]
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    
    # Metadata
    confidence_score = models.FloatField(default=0.0)
    importance_score = models.FloatField(default=0.0)
    
    # Supporting data
    supporting_data = models.JSONField(default=dict)
    related_charts = models.ManyToManyField(Chart, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-importance_score', '-created_at']
        db_table = 'analytics_insight'
    
    def __str__(self):
        return self.title


class AnalysisTemplate(models.Model):
    """
    Model for storing reusable analysis templates
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Template configuration
    analysis_type = models.CharField(max_length=20, choices=Analysis.ANALYSIS_TYPES)
    configuration = models.JSONField(default=dict)
    
    # Template settings
    is_public = models.BooleanField(default=False)
    is_system_template = models.BooleanField(default=False)
    
    # Usage statistics
    usage_count = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
        db_table = 'analytics_analysistemplate'
    
    def __str__(self):
        return self.name

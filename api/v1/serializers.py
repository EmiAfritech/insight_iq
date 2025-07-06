from rest_framework import serializers
from analytics.models import DataSet, Analysis, Chart, Insight
from dashboards.models import Dashboard, DashboardWidget


class DataSetSerializer(serializers.ModelSerializer):
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = DataSet
        fields = [
            'id', 'name', 'description', 'file', 'file_size', 'file_size_mb',
            'file_type', 'total_rows', 'total_columns', 'columns_info',
            'status', 'created_at', 'updated_at', 'tags'
        ]
        read_only_fields = ['id', 'file_size', 'file_type', 'total_rows', 'total_columns', 'columns_info', 'status']


class ChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chart
        fields = [
            'id', 'name', 'description', 'chart_type', 'data',
            'configuration', 'width', 'height', 'is_interactive',
            'created_at', 'updated_at'
        ]


class InsightSerializer(serializers.ModelSerializer):
    related_charts = ChartSerializer(many=True, read_only=True)
    
    class Meta:
        model = Insight
        fields = [
            'id', 'title', 'description', 'insight_type',
            'confidence_score', 'importance_score', 'supporting_data',
            'related_charts', 'is_verified', 'created_at', 'updated_at'
        ]


class AnalysisSerializer(serializers.ModelSerializer):
    dataset_name = serializers.CharField(source='dataset.name', read_only=True)
    charts = ChartSerializer(source='chart_objects', many=True, read_only=True)
    insights = InsightSerializer(source='insight_objects', many=True, read_only=True)
    
    class Meta:
        model = Analysis
        fields = [
            'id', 'dataset', 'dataset_name', 'name', 'description',
            'analysis_type', 'configuration', 'selected_columns',
            'results', 'charts', 'insights', 'ai_summary',
            'ai_insights', 'ai_recommendations', 'status',
            'execution_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'results', 'ai_summary', 'ai_insights', 'ai_recommendations', 'status', 'execution_time']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'title', 'widget_type', 'chart', 'dataset',
            'analysis', 'configuration', 'custom_data',
            'position_x', 'position_y', 'width', 'height',
            'is_visible', 'auto_refresh'
        ]


class DashboardSerializer(serializers.ModelSerializer):
    widgets = DashboardWidgetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dashboard
        fields = [
            'id', 'name', 'description', 'layout', 'theme',
            'is_public', 'auto_refresh', 'refresh_interval',
            'widgets', 'created_at', 'updated_at', 'view_count'
        ]
        read_only_fields = ['id', 'view_count']


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False)


class QuickAnalysisSerializer(serializers.Serializer):
    dataset_id = serializers.UUIDField()
    analysis_type = serializers.ChoiceField(choices=Analysis.ANALYSIS_TYPES)
    selected_columns = serializers.ListField(child=serializers.CharField(), required=False)
    configuration = serializers.DictField(required=False)

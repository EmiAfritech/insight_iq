from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dataset management
    path('', views.DataSetListView.as_view(), name='dataset_list'),
    path('upload/', views.DataSetUploadView.as_view(), name='dataset_upload'),
    path('dataset/<uuid:pk>/', views.DataSetDetailView.as_view(), name='dataset_detail'),
    path('dataset/<uuid:pk>/edit/', views.DataSetUpdateView.as_view(), name='dataset_edit'),
    path('dataset/<uuid:pk>/delete/', views.DataSetDeleteView.as_view(), name='dataset_delete'),
    path('dataset/<uuid:pk>/preview/', views.DataSetPreviewView.as_view(), name='dataset_preview'),
    
    # Analysis management
    path('analyses/', views.AnalysisListView.as_view(), name='analysis_list'),
    path('analyze/<uuid:dataset_id>/', views.AnalysisCreateView.as_view(), name='analysis_create'),
    path('analysis/<uuid:pk>/', views.AnalysisDetailView.as_view(), name='analysis_detail'),
    path('analysis/<uuid:pk>/edit/', views.AnalysisUpdateView.as_view(), name='analysis_edit'),
    path('analysis/<uuid:pk>/delete/', views.AnalysisDeleteView.as_view(), name='analysis_delete'),
    path('analysis/<uuid:pk>/run/', views.AnalysisRunView.as_view(), name='analysis_run'),
    path('analysis/<uuid:pk>/results/', views.AnalysisResultsView.as_view(), name='analysis_results'),
    
    # Chart management
    path('chart/<uuid:pk>/', views.ChartDetailView.as_view(), name='chart_detail'),
    path('chart/<uuid:pk>/edit/', views.ChartUpdateView.as_view(), name='chart_edit'),
    path('chart/<uuid:pk>/data/', views.ChartDataView.as_view(), name='chart_data'),
    
    # Insight management
    path('insights/', views.InsightListView.as_view(), name='insight_list'),
    path('insight/<uuid:pk>/', views.InsightDetailView.as_view(), name='insight_detail'),
    path('insight/<uuid:pk>/verify/', views.InsightVerifyView.as_view(), name='insight_verify'),
    path('insight/<uuid:pk>/hide/', views.InsightHideView.as_view(), name='insight_hide'),
    
    # Template management
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('template/<uuid:pk>/', views.TemplateDetailView.as_view(), name='template_detail'),
    path('template/<uuid:pk>/use/', views.TemplateUseView.as_view(), name='template_use'),
    
    # API endpoints
    path('api/dataset/<uuid:pk>/columns/', views.DataSetColumnsAPIView.as_view(), name='api_dataset_columns'),
    path('api/analysis/<uuid:pk>/status/', views.AnalysisStatusAPIView.as_view(), name='api_analysis_status'),
    path('api/chart/<uuid:pk>/export/', views.ChartExportAPIView.as_view(), name='api_chart_export'),
]

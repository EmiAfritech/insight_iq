from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'datasets', views.DataSetViewSet)
router.register(r'analyses', views.AnalysisViewSet)
router.register(r'insights', views.InsightViewSet)
router.register(r'dashboards', views.DashboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('upload/', views.FileUploadView.as_view(), name='file_upload'),
    path('analyze/', views.QuickAnalysisView.as_view(), name='quick_analysis'),
    path('export/<uuid:analysis_id>/', views.ExportAnalysisView.as_view(), name='export_analysis'),
    
    # Additional API endpoints for template functionality
    path('dashboards/<uuid:dashboard_id>/duplicate/', views.duplicate_dashboard, name='duplicate_dashboard'),
    path('reports/shares/<uuid:share_id>/revoke/', views.revoke_share, name='revoke_share'),
    path('reports/export/<uuid:export_id>/status/', views.export_status, name='export_status'),
    path('users/export-data/', views.export_user_data, name='export_user_data'),
]

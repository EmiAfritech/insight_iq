from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Report management
    path('', views.report_list, name='report_list'),
    path('create/', views.report_create, name='report_create'),
    path('<uuid:report_id>/', views.report_detail, name='report_detail'),
    path('<uuid:report_id>/edit/', views.report_edit, name='report_edit'),
    path('<uuid:report_id>/export/', views.report_export, name='report_export'),
    path('<uuid:report_id>/share/', views.report_share, name='report_share'),
    path('<uuid:report_id>/comment/', views.report_comment, name='report_comment'),
    path('<uuid:report_id>/generate/', views.report_generate, name='report_generate'),
    
    # Report templates
    path('templates/', views.report_template_list, name='template_list'),
    path('templates/create/', views.report_template_create, name='template_create'),
    
    # Public access
    path('shared/<str:share_token>/', views.public_report_view, name='public_report'),
]

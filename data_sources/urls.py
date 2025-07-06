from django.urls import path
from . import views

app_name = 'data_sources'

urlpatterns = [
    path('', views.DataSourceListView.as_view(), name='list'),
    path('create/', views.DataSourceCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.DataSourceDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.DataSourceUpdateView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.DataSourceDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/test/', views.DataSourceTestView.as_view(), name='test'),
    path('<uuid:pk>/pull/', views.DataPullCreateView.as_view(), name='pull'),
    path('pull/<uuid:pk>/', views.DataPullDetailView.as_view(), name='pull_detail'),
    path('templates/', views.DataSourceTemplateListView.as_view(), name='templates'),
    path('templates/<uuid:pk>/', views.DataSourceTemplateDetailView.as_view(), name='template_detail'),
]

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardHomeView.as_view(), name='home'),
    path('list/', views.DashboardListView.as_view(), name='list'),
    path('create/', views.DashboardCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.DashboardDetailView.as_view(), name='detail'),
    path('<uuid:pk>/edit/', views.DashboardEditView.as_view(), name='edit'),
    path('<uuid:pk>/delete/', views.DashboardDeleteView.as_view(), name='delete'),
    path('<uuid:pk>/share/', views.DashboardShareView.as_view(), name='share'),
    path('<uuid:pk>/widget/add/', views.WidgetCreateView.as_view(), name='widget_add'),
    path('widget/<uuid:pk>/edit/', views.WidgetEditView.as_view(), name='widget_edit'),
    path('widget/<uuid:pk>/delete/', views.WidgetDeleteView.as_view(), name='widget_delete'),
    path('templates/', views.DashboardTemplateListView.as_view(), name='templates'),
    path('template/<uuid:pk>/', views.DashboardTemplateDetailView.as_view(), name='template_detail'),
    path('template/<uuid:pk>/use/', views.DashboardTemplateUseView.as_view(), name='template_use'),
]

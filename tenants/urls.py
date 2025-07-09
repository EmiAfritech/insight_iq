from django.urls import path
from . import views
from . import debug_views

app_name = 'tenants'

urlpatterns = [
    path('register/', views.TenantCreateView.as_view(), name='register'),
    path('create/', views.TenantCreateView.as_view(), name='create'),
    path('setup/', views.TenantSetupView.as_view(), name='setup'),
    path('switch/', views.TenantSwitchView.as_view(), name='switch'),
    path('settings/', views.TenantSettingsView.as_view(), name='settings'),
    path('users/', views.TenantUserListView.as_view(), name='users'),
    path('users/invite/', views.TenantUserInviteView.as_view(), name='invite_user'),
    path('users/<int:pk>/edit/', views.TenantUserEditView.as_view(), name='edit_user'),
    path('users/<int:pk>/delete/', views.TenantUserDeleteView.as_view(), name='delete_user'),
    path('debug/status/', debug_views.user_status, name='debug_status'),
    path('debug/user-status/', debug_views.user_status_debug, name='debug_user_status'),
]

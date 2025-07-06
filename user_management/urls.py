from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    path('', views.UserListView.as_view(), name='list'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('activity/', views.UserActivityView.as_view(), name='activity'),
]

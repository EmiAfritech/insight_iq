from django.shortcuts import render
from django.views.generic import ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from tenants.mixins import TenantRequiredMixin, PermissionRequiredMixin
from tenants.models import TenantUser


class UserListView(TenantRequiredMixin, LoginRequiredMixin, ListView):
    """
    List all users in the tenant
    """
    model = TenantUser
    template_name = 'user_management/list.html'
    context_object_name = 'users'
    paginate_by = 20
    required_permission = 'manage_users'
    
    def get_queryset(self):
        return TenantUser.objects.filter(
            tenant=self.tenant,
            is_active=True
        ).select_related('user')


class UserProfileView(TenantRequiredMixin, UpdateView):
    """
    User profile view and edit
    """
    model = TenantUser
    template_name = 'user_management/profile.html'
    fields = ['phone', 'department', 'job_title', 'profile_picture']
    success_url = reverse_lazy('user_management:profile')
    
    def get_object(self):
        return TenantUser.objects.get(user=self.request.user, tenant=self.tenant)
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class UserSettingsView(TenantRequiredMixin, TemplateView):
    """
    User settings and preferences
    """
    template_name = 'user_management/settings.html'


class UserActivityView(TenantRequiredMixin, TemplateView):
    """
    User activity and audit log
    """
    template_name = 'user_management/activity.html'

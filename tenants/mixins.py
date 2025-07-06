from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import TenantUser


class TenantMixin:
    """
    Mixin to add tenant context to views
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                self.tenant_user = TenantUser.objects.get(user=request.user, is_active=True)
                self.tenant = self.tenant_user.tenant
                request.tenant_user = self.tenant_user
                request.tenant = self.tenant
            except TenantUser.DoesNotExist:
                self.tenant_user = None
                self.tenant = None
        return super().dispatch(request, *args, **kwargs)


class TenantRequiredMixin(LoginRequiredMixin, TenantMixin):
    """
    Mixin to ensure user belongs to a tenant
    """
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if not hasattr(self, 'tenant_user') or self.tenant_user is None:
            raise PermissionDenied("You are not associated with any tenant.")
        return response


class PermissionRequiredMixin(TenantRequiredMixin):
    """
    Mixin to check specific tenant permissions
    """
    required_permission = None
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if self.required_permission:
            if self.required_permission == 'upload_data' and not self.tenant_user.can_upload_data:
                raise PermissionDenied("You don't have permission to upload data.")
            elif self.required_permission == 'create_reports' and not self.tenant_user.can_create_reports:
                raise PermissionDenied("You don't have permission to create reports.")
            elif self.required_permission == 'view_all_data' and not self.tenant_user.can_view_all_data:
                raise PermissionDenied("You don't have permission to view all data.")
            elif self.required_permission == 'manage_users' and not self.tenant_user.can_manage_users:
                raise PermissionDenied("You don't have permission to manage users.")
            elif self.required_permission == 'manage_settings' and not self.tenant_user.can_manage_settings:
                raise PermissionDenied("You don't have permission to manage settings.")
        
        return response


class RoleRequiredMixin(TenantRequiredMixin):
    """
    Mixin to check user role
    """
    required_roles = None
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        if self.required_roles:
            if isinstance(self.required_roles, str):
                required_roles = [self.required_roles]
            else:
                required_roles = self.required_roles
            
            if self.tenant_user.role not in required_roles:
                raise PermissionDenied(f"You need one of these roles: {', '.join(required_roles)}")
        
        return response

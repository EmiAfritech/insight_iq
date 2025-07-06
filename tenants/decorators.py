from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import TenantUser


def tenant_required(view_func):
    """
    Decorator to ensure user belongs to a tenant
    """
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            tenant_user = TenantUser.objects.get(user=request.user, is_active=True)
            request.tenant_user = tenant_user
            request.tenant = tenant_user.tenant
            return view_func(request, *args, **kwargs)
        except TenantUser.DoesNotExist:
            raise Http404("You are not associated with any tenant.")
    return wrapper


def permission_required(permission):
    """
    Decorator to check specific tenant permissions
    """
    def decorator(view_func):
        @tenant_required
        def wrapper(request, *args, **kwargs):
            tenant_user = request.tenant_user
            
            if permission == 'upload_data' and not tenant_user.can_upload_data:
                raise Http404("You don't have permission to upload data.")
            elif permission == 'create_reports' and not tenant_user.can_create_reports:
                raise Http404("You don't have permission to create reports.")
            elif permission == 'view_all_data' and not tenant_user.can_view_all_data:
                raise Http404("You don't have permission to view all data.")
            elif permission == 'manage_users' and not tenant_user.can_manage_users:
                raise Http404("You don't have permission to manage users.")
            elif permission == 'manage_settings' and not tenant_user.can_manage_settings:
                raise Http404("You don't have permission to manage settings.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def role_required(required_roles):
    """
    Decorator to check user role
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(view_func):
        @tenant_required
        def wrapper(request, *args, **kwargs):
            tenant_user = request.tenant_user
            
            if tenant_user.role not in required_roles:
                raise Http404(f"You need one of these roles: {', '.join(required_roles)}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

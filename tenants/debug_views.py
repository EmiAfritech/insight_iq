"""Debug views for tenant functionality"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import TenantUser


@login_required
def user_status(request):
    """Debug view to show user's tenant status"""
    try:
        tenant_user = TenantUser.objects.get(user=request.user)
        tenant_info = {
            'has_tenant': True,
            'tenant_name': tenant_user.tenant.name,
            'role': tenant_user.role,
            'tenant_id': tenant_user.tenant.id
        }
    except TenantUser.DoesNotExist:
        tenant_info = {
            'has_tenant': False,
            'tenant_name': None,
            'role': None,
            'tenant_id': None
        }
    
    return JsonResponse({
        'user': request.user.email,
        'is_authenticated': request.user.is_authenticated,
        'tenant_info': tenant_info
    })


def user_status_debug(request):
    """Debug view to check user tenant status"""
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'authenticated': False,
            'message': 'User not authenticated'
        })
    
    try:
        tenant_user = TenantUser.objects.get(user=request.user)
        return JsonResponse({
            'authenticated': True,
            'has_tenant': True,
            'tenant_name': tenant_user.tenant.name,
            'tenant_id': str(tenant_user.tenant.id),
            'user_role': tenant_user.role,
            'is_active': tenant_user.is_active,
            'message': 'User has valid tenant'
        })
    except TenantUser.DoesNotExist:
        return JsonResponse({
            'authenticated': True,
            'has_tenant': False,
            'message': 'User has no tenant association'
        })

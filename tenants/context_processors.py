from .models import TenantUser


def tenant_context(request):
    """
    Context processor to add tenant information to templates
    """
    context = {}
    
    if request.user.is_authenticated:
        try:
            tenant_user = TenantUser.objects.get(user=request.user, is_active=True)
            context.update({
                'tenant_user': tenant_user,
                'tenant': tenant_user.tenant,
                'user_role': tenant_user.role,
                'user_permissions': {
                    'can_upload_data': tenant_user.can_upload_data,
                    'can_create_reports': tenant_user.can_create_reports,
                    'can_view_all_data': tenant_user.can_view_all_data,
                    'can_manage_users': tenant_user.can_manage_users,
                    'can_manage_settings': tenant_user.can_manage_settings,
                }
            })
        except TenantUser.DoesNotExist:
            pass
    
    return context

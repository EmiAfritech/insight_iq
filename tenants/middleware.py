"""
Tenant middleware for handling user redirects and tenant context.
"""
import logging
from django.shortcuts import redirect
from django.contrib.auth.models import AnonymousUser
from .models import TenantUser

logger = logging.getLogger(__name__)


class TenantRedirectMiddleware:
    """
    Middleware to redirect authenticated users without tenants to tenant creation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called.
        
        return response

    def process_view(self, request, _view_func, _view_args, _view_kwargs):
        """
        Check if authenticated user needs to be redirected to tenant creation
        """
        # Skip for anonymous users
        if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
            logger.info("Skipping middleware for anonymous user on path: %s", request.path)
            return None
            
        logger.info("Processing middleware for user %s on path: %s",
                   request.user.email, request.path)
            
        # Skip for certain URLs (to avoid redirect loops)
        skip_paths = [
            '/tenants/register/',
            '/tenants/create/',
            '/tenants/setup/',
            '/tenants/debug/',
            '/accounts/logout/',
            '/accounts/login/',
            '/accounts/signup/',
            '/admin/',
            '/static/',
            '/media/',
            '/api/',
        ]
        
        # Check if current path should be skipped
        for path in skip_paths:
            if request.path.startswith(path):
                logger.info("Skipping middleware for path: %s", request.path)
                return None
        
        # Check if user has a tenant
        try:
            tenant_users = TenantUser.objects.filter(user=request.user, is_active=True)
            
            if tenant_users.exists():
                # User has tenant(s), pick the first active one
                tenant_user = tenant_users.first()
                logger.info("User %s has tenant: %s", request.user.email, tenant_user.tenant.name)
                
                # Store tenant in session for consistency
                request.session['current_tenant_id'] = str(tenant_user.tenant.id)
                
                # If user is on root path and has a tenant, redirect to dashboard
                if request.path in ['/', '/dashboard/', '/tenants/register/']:
                    logger.info("Redirecting user %s to dashboard", request.user.email)
                    return redirect('dashboards:home')
                
                # User has a tenant, continue normally
                return None
            else:
                # User doesn't have an active tenant, redirect to tenant creation
                logger.info("User %s has no active tenant, redirecting to registration", 
                           request.user.email)
                return redirect('tenants:register')
        except Exception as e:
            logger.error("Error checking tenant for user %s: %s", request.user.email, str(e))
            return redirect('tenants:register')

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Tenant, TenantUser
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Tenant)
def create_tenant_schema(sender, instance, created, **kwargs):
    """
    Create tenant schema after tenant is created
    """
    if created:
        logger.info(f"Created new tenant: {instance.name}")
        # Additional setup logic can be added here


@receiver(post_delete, sender=Tenant)
def delete_tenant_schema(sender, instance, **kwargs):
    """
    Clean up after tenant deletion
    """
    logger.info(f"Deleted tenant: {instance.name}")


@receiver(post_save, sender=User)
def create_tenant_user_profile(sender, instance, created, **kwargs):
    """
    Create TenantUser profile when a new user is created
    """
    if created:
        # This will be handled by the registration process
        pass


@receiver(post_save, sender=TenantUser)
def update_user_permissions(sender, instance, created, **kwargs):
    """
    Update user permissions based on role
    """
    if created or 'role' in kwargs.get('update_fields', []):
        user = instance.user
        
        # Set permissions based on role
        if instance.role == 'owner':
            instance.can_upload_data = True
            instance.can_create_reports = True
            instance.can_view_all_data = True
            instance.can_manage_users = True
            instance.can_manage_settings = True
        elif instance.role == 'admin':
            instance.can_upload_data = True
            instance.can_create_reports = True
            instance.can_view_all_data = True
            instance.can_manage_users = True
            instance.can_manage_settings = False
        elif instance.role == 'analyst':
            instance.can_upload_data = True
            instance.can_create_reports = True
            instance.can_view_all_data = False
            instance.can_manage_users = False
            instance.can_manage_settings = False
        elif instance.role == 'viewer':
            instance.can_upload_data = False
            instance.can_create_reports = False
            instance.can_view_all_data = False
            instance.can_manage_users = False
            instance.can_manage_settings = False
        elif instance.role == 'guest':
            instance.can_upload_data = False
            instance.can_create_reports = False
            instance.can_view_all_data = False
            instance.can_manage_users = False
            instance.can_manage_settings = False
        
        # Save without triggering signals again
        TenantUser.objects.filter(pk=instance.pk).update(
            can_upload_data=instance.can_upload_data,
            can_create_reports=instance.can_create_reports,
            can_view_all_data=instance.can_view_all_data,
            can_manage_users=instance.can_manage_users,
            can_manage_settings=instance.can_manage_settings
        )

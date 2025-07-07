from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView, TemplateView, FormView
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import Tenant, Domain, TenantUser
from .forms import SimpleTenantCreationForm, TenantUserForm, TenantSettingsForm, UserInviteForm


class TenantCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new tenant
    """
    model = Tenant
    form_class = SimpleTenantCreationForm
    template_name = 'tenants/create_tenant.html'
    success_url = reverse_lazy('tenants:setup')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Create domain for tenant
        domain_name = form.cleaned_data.get('domain_name')
        if not domain_name:
            domain_name = self.object.name.lower().replace(' ', '-')
        tenant_domain = getattr(settings, 'TENANT_DOMAIN', 'localhost')
        Domain.objects.create(
            domain=f"{domain_name}.{tenant_domain}",
            tenant=self.object,
            is_primary=True
        )
        
        # Create tenant user for the current user as owner
        TenantUser.objects.create(
            user=self.request.user,
            tenant=self.object,
            role='owner'
        )
        
        messages.success(self.request, f"Organization '{self.object.name}' created successfully!")
        return response


class TenantSetupView(LoginRequiredMixin, TemplateView):
    """
    View for tenant setup and onboarding
    """
    template_name = 'tenants/setup.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            tenant_user = TenantUser.objects.get(user=self.request.user)
            context['tenant'] = tenant_user.tenant
            context['is_owner'] = tenant_user.is_owner
        except TenantUser.DoesNotExist:
            context['tenant'] = None
        return context


class TenantSwitchView(LoginRequiredMixin, TemplateView):
    """
    View for switching between tenants (if user belongs to multiple)
    """
    template_name = 'tenants/switch.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenants'] = TenantUser.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('tenant')
        return context


class TenantSettingsView(LoginRequiredMixin, UpdateView):
    """
    View for updating tenant settings
    """
    model = Tenant
    form_class = TenantSettingsForm
    template_name = 'tenants/settings.html'
    success_url = reverse_lazy('tenants:settings')
    
    def get_object(self):
        tenant_user = get_object_or_404(TenantUser, user=self.request.user)
        return tenant_user.tenant
    
    def dispatch(self, request, *args, **kwargs):
        try:
            tenant_user = TenantUser.objects.get(user=request.user)
            if not tenant_user.can_manage_settings:
                messages.error(request, "You don't have permission to manage tenant settings.")
                return redirect('dashboard:home')
        except TenantUser.DoesNotExist:
            messages.error(request, "You are not associated with any tenant.")
            return redirect('core:landing')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, "Tenant settings updated successfully!")
        return super().form_valid(form)


class TenantUserListView(LoginRequiredMixin, ListView):
    """
    View for listing tenant users
    """
    model = TenantUser
    template_name = 'tenants/users.html'
    context_object_name = 'tenant_users'
    paginate_by = 20
    
    def get_queryset(self):
        tenant_user = get_object_or_404(TenantUser, user=self.request.user)
        return TenantUser.objects.filter(
            tenant=tenant_user.tenant
        ).select_related('user', 'tenant').order_by('-created_at')
    
    def dispatch(self, request, *args, **kwargs):
        try:
            tenant_user = TenantUser.objects.get(user=request.user)
            if not tenant_user.can_manage_users:
                messages.error(request, "You don't have permission to manage users.")
                return redirect('dashboard:home')
        except TenantUser.DoesNotExist:
            messages.error(request, "You are not associated with any tenant.")
            return redirect('core:landing')
        return super().dispatch(request, *args, **kwargs)


class TenantUserInviteView(LoginRequiredMixin, FormView):
    """
    View for inviting new users to tenant
    """
    form_class = UserInviteForm
    template_name = 'tenants/invite_user.html'
    success_url = reverse_lazy('tenants:users')
    
    def dispatch(self, request, *args, **kwargs):
        try:
            self.tenant_user = TenantUser.objects.get(user=request.user)
            if not self.tenant_user.can_manage_users:
                messages.error(request, "You don't have permission to invite users.")
                return redirect('dashboard:home')
        except TenantUser.DoesNotExist:
            messages.error(request, "You are not associated with any tenant.")
            return redirect('core:landing')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        role = form.cleaned_data['role']
        
        # Check if user already exists
        try:
            user = User.objects.get(email=email)
            # Check if user is already in this tenant
            if TenantUser.objects.filter(user=user, tenant=self.tenant_user.tenant).exists():
                messages.error(self.request, "User is already a member of this tenant.")
                return self.form_invalid(form)
            
            # User exists but not in this tenant - create TenantUser
            tenant_user = TenantUser.objects.create(
                user=user,
                tenant=self.tenant_user.tenant,
                role=role
            )
            
        except User.DoesNotExist:
            # Create new user with random password
            user = User.objects.create_user(
                username=email,
                email=email,
                password=get_random_string(12),
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', '')
            )
            user.is_active = False  # User needs to activate account
            user.save()
            
            # Create tenant user
            tenant_user = TenantUser.objects.create(
                user=user,
                tenant=self.tenant_user.tenant,
                role=role
            )
        
        # Send invitation email
        self.send_invitation_email(user, tenant_user)
        
        messages.success(self.request, f"Invitation sent to {email}!")
        return super().form_valid(form)
    
    def send_invitation_email(self, user, tenant_user):
        """
        Send invitation email to new user
        """
        subject = f"You've been invited to join {tenant_user.tenant.company_name}"
        message = f"""
        Hi {user.first_name or user.email},
        
        You've been invited to join {tenant_user.tenant.company_name} on InsightIQ.
        
        Please click the link below to accept the invitation and set up your account:
        
        {settings.DEFAULT_DOMAIN}/accounts/activate/{user.pk}/
        
        Your role: {tenant_user.get_role_display()}
        
        Best regards,
        The InsightIQ Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class TenantUserEditView(LoginRequiredMixin, UpdateView):
    """
    View for editing tenant user
    """
    model = TenantUser
    form_class = TenantUserForm
    template_name = 'tenants/edit_user.html'
    success_url = reverse_lazy('tenants:users')
    
    def get_queryset(self):
        tenant_user = get_object_or_404(TenantUser, user=self.request.user)
        return TenantUser.objects.filter(tenant=tenant_user.tenant)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            tenant_user = TenantUser.objects.get(user=request.user)
            if not tenant_user.can_manage_users:
                messages.error(request, "You don't have permission to edit users.")
                return redirect('dashboard:home')
        except TenantUser.DoesNotExist:
            messages.error(request, "You are not associated with any tenant.")
            return redirect('core:landing')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, "User updated successfully!")
        return super().form_valid(form)


class TenantUserDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting tenant user
    """
    model = TenantUser
    template_name = 'tenants/delete_user.html'
    success_url = reverse_lazy('tenants:users')
    
    def get_queryset(self):
        tenant_user = get_object_or_404(TenantUser, user=self.request.user)
        return TenantUser.objects.filter(tenant=tenant_user.tenant)
    
    def dispatch(self, request, *args, **kwargs):
        try:
            tenant_user = TenantUser.objects.get(user=request.user)
            if not tenant_user.can_manage_users:
                messages.error(request, "You don't have permission to delete users.")
                return redirect('dashboard:home')
        except TenantUser.DoesNotExist:
            messages.error(request, "You are not associated with any tenant.")
            return redirect('core:landing')
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "User removed successfully!")
        return super().delete(request, *args, **kwargs)

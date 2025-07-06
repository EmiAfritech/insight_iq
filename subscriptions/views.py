from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from tenants.mixins import TenantRequiredMixin, PermissionRequiredMixin
from .models import SubscriptionPlan, Subscription, SubscriptionUsage


class SubscriptionPlanListView(ListView):
    """
    List all available subscription plans
    """
    model = SubscriptionPlan
    template_name = 'subscriptions/plans.html'
    context_object_name = 'plans'
    
    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True)


class CurrentSubscriptionView(TenantRequiredMixin, DetailView):
    """
    View current subscription details
    """
    model = Subscription
    template_name = 'subscriptions/current.html'
    context_object_name = 'subscription'
    
    def get_object(self):
        return Subscription.objects.get(tenant=self.tenant)


class UpgradeSubscriptionView(TenantRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Upgrade subscription
    """
    template_name = 'subscriptions/upgrade.html'
    required_permission = 'manage_settings'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = SubscriptionPlan.objects.filter(is_active=True)
        try:
            context['current_subscription'] = Subscription.objects.get(tenant=self.tenant)
        except Subscription.DoesNotExist:
            context['current_subscription'] = None
        return context


class CancelSubscriptionView(TenantRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    Cancel subscription
    """
    template_name = 'subscriptions/cancel.html'
    required_permission = 'manage_settings'


class UsageView(TenantRequiredMixin, TemplateView):
    """
    View subscription usage
    """
    template_name = 'subscriptions/usage.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            subscription = Subscription.objects.get(tenant=self.tenant)
            context['subscription'] = subscription
            context['usage_records'] = SubscriptionUsage.objects.filter(
                subscription=subscription
            ).order_by('-usage_date')[:30]
        except Subscription.DoesNotExist:
            context['subscription'] = None
        return context

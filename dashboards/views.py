from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import models
from tenants.mixins import TenantRequiredMixin, PermissionRequiredMixin
from .models import Dashboard, DashboardWidget, DashboardTemplate, DashboardShare, DashboardView
from analytics.models import DataSet, Analysis


class DashboardHomeView(TenantRequiredMixin, TemplateView):
    """
    Dashboard home page showing overview and recent dashboards
    """
    template_name = 'dashboards/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get user's dashboards
        user_dashboards = Dashboard.objects.filter(
            created_by=self.request.user
        ).order_by('-last_viewed')[:5]
        
        # Get shared dashboards
        shared_dashboards = Dashboard.objects.filter(
            shares__shared_with=self.request.user,
            shares__is_active=True
        ).order_by('-last_viewed')[:5]
        
        # Get recent datasets
        recent_datasets = DataSet.objects.filter(
            uploaded_by=self.request.user,
            status='ready'
        ).order_by('-created_at')[:5]
        
        # Get recent analyses
        recent_analyses = Analysis.objects.filter(
            created_by=self.request.user,
            status='completed'
        ).order_by('-created_at')[:5]
        
        context.update({
            'user_dashboards': user_dashboards,
            'shared_dashboards': shared_dashboards,
            'recent_datasets': recent_datasets,
            'recent_analyses': recent_analyses,
            'total_dashboards': Dashboard.objects.filter(created_by=self.request.user).count(),
            'total_datasets': DataSet.objects.filter(uploaded_by=self.request.user).count(),
            'total_analyses': Analysis.objects.filter(created_by=self.request.user).count(),
        })
        
        return context


class DashboardListView(TenantRequiredMixin, ListView):
    """
    List all dashboards for the user
    """
    model = Dashboard
    template_name = 'dashboards/list.html'
    context_object_name = 'dashboards'
    paginate_by = 20
    
    def get_queryset(self):
        return Dashboard.objects.filter(
            created_by=self.request.user
        ).order_by('-updated_at')


class DashboardCreateView(TenantRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Create a new dashboard
    """
    model = Dashboard
    template_name = 'dashboards/create.html'
    fields = ['name', 'description', 'theme', 'auto_refresh', 'refresh_interval']
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.tenant = self.request.tenant
        messages.success(self.request, 'Dashboard created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboards:detail', kwargs={'pk': self.object.pk})


class DashboardDetailView(TenantRequiredMixin, DetailView):
    """
    View dashboard details and widgets
    """
    model = Dashboard
    template_name = 'dashboards/detail.html'
    context_object_name = 'dashboard'
    
    def get_queryset(self):
        return Dashboard.objects.filter(
            models.Q(created_by=self.request.user) |
            models.Q(shares__shared_with=self.request.user, shares__is_active=True)
        ).distinct()
    
    def get_object(self):
        obj = super().get_object()
        
        # Track dashboard view
        DashboardView.objects.create(
            dashboard=obj,
            user=self.request.user,
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        # Update dashboard view count and last viewed
        obj.view_count += 1
        obj.last_viewed = timezone.now()
        obj.save(update_fields=['view_count', 'last_viewed'])
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widgets'] = self.object.widgets.filter(is_visible=True)
        return context


class DashboardEditView(TenantRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Edit dashboard
    """
    model = Dashboard
    template_name = 'dashboards/edit.html'
    fields = ['name', 'description', 'theme', 'auto_refresh', 'refresh_interval', 'is_public']
    
    def get_queryset(self):
        return Dashboard.objects.filter(created_by=self.request.user, tenant=self.request.tenant)
    
    def form_valid(self, form):
        messages.success(self.request, 'Dashboard updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboards:detail', kwargs={'pk': self.object.pk})


class DashboardDeleteView(TenantRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Delete dashboard
    """
    model = Dashboard
    template_name = 'dashboards/delete.html'
    success_url = reverse_lazy('dashboards:list')
    
    def get_queryset(self):
        return Dashboard.objects.filter(created_by=self.request.user, tenant=self.request.tenant)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Dashboard deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DashboardShareView(TenantRequiredMixin, TemplateView):
    """
    Share dashboard with other users
    """
    template_name = 'dashboards/share.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dashboard = get_object_or_404(Dashboard, pk=self.kwargs['pk'], created_by=self.request.user)
        context['dashboard'] = dashboard
        context['shares'] = dashboard.shares.all()
        return context


class WidgetCreateView(TenantRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Create a new widget for dashboard
    """
    model = DashboardWidget
    template_name = 'dashboards/widget_create.html'
    fields = ['title', 'widget_type', 'chart', 'dataset', 'analysis', 'configuration', 
              'width', 'height', 'position_x', 'position_y']
    
    def form_valid(self, form):
        dashboard = get_object_or_404(Dashboard, pk=self.kwargs['pk'], created_by=self.request.user, tenant=self.request.tenant)
        form.instance.dashboard = dashboard
        messages.success(self.request, 'Widget created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboards:detail', kwargs={'pk': self.kwargs['pk']})


class WidgetEditView(TenantRequiredMixin, LoginRequiredMixin, UpdateView):
    """
    Edit dashboard widget
    """
    model = DashboardWidget
    template_name = 'dashboards/widget_edit.html'
    fields = ['title', 'widget_type', 'chart', 'dataset', 'analysis', 'configuration', 
              'width', 'height', 'position_x', 'position_y', 'is_visible']
    
    def get_queryset(self):
        return DashboardWidget.objects.filter(dashboard__created_by=self.request.user, dashboard__tenant=self.request.tenant)
    
    def form_valid(self, form):
        messages.success(self.request, 'Widget updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboards:detail', kwargs={'pk': self.object.dashboard.pk})


class WidgetDeleteView(TenantRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Delete dashboard widget
    """
    model = DashboardWidget
    template_name = 'dashboards/widget_delete.html'
    
    def get_queryset(self):
        return DashboardWidget.objects.filter(dashboard__created_by=self.request.user, dashboard__tenant=self.request.tenant)
    
    def delete(self, request, *args, **kwargs):
        dashboard_pk = self.get_object().dashboard.pk
        messages.success(request, 'Widget deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('dashboards:detail', kwargs={'pk': self.object.dashboard.pk})


class DashboardTemplateListView(TenantRequiredMixin, ListView):
    """
    List dashboard templates
    """
    model = DashboardTemplate
    template_name = 'dashboards/templates.html'
    context_object_name = 'templates'
    paginate_by = 20


class DashboardTemplateDetailView(TenantRequiredMixin, DetailView):
    """
    View dashboard template details
    """
    model = DashboardTemplate
    template_name = 'dashboards/template_detail.html'
    context_object_name = 'template'


class DashboardTemplateUseView(TenantRequiredMixin, LoginRequiredMixin, TemplateView):
    """
    Use dashboard template to create new dashboard
    """
    template_name = 'dashboards/template_use.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = get_object_or_404(DashboardTemplate, pk=self.kwargs['pk'])
        context['template'] = template
        return context
    
    def post(self, request, *args, **kwargs):
        template = get_object_or_404(DashboardTemplate, pk=self.kwargs['pk'])
        
        # Create dashboard from template
        dashboard = Dashboard.objects.create(
            name=f"{template.name} - {timezone.now().strftime('%Y-%m-%d')}",
            description=template.description,
            created_by=request.user,
            tenant=request.tenant,
            layout=template.layout_template
        )
        
        # Create widgets from template
        for widget_data in template.widgets_template:
            DashboardWidget.objects.create(
                dashboard=dashboard,
                title=widget_data.get('title', 'Widget'),
                widget_type=widget_data.get('widget_type', 'chart'),
                configuration=widget_data.get('configuration', {}),
                width=widget_data.get('width', 4),
                height=widget_data.get('height', 3),
                position_x=widget_data.get('position_x', 0),
                position_y=widget_data.get('position_y', 0)
            )
        
        # Update template usage count
        template.usage_count += 1
        template.save(update_fields=['usage_count'])
        
        messages.success(request, f'Dashboard created from template "{template.name}"!')
        return redirect('dashboards:detail', pk=dashboard.pk)

from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from tenants.mixins import TenantRequiredMixin, PermissionRequiredMixin
from .models import DataSource, DataSourceConnection, DataPull, DataSourceTemplate


class DataSourceListView(TenantRequiredMixin, ListView):
    """
    List all data sources for the tenant
    """
    model = DataSource
    template_name = 'data_sources/list.html'
    context_object_name = 'data_sources'
    paginate_by = 20
    
    def get_queryset(self):
        return DataSource.objects.filter(
            created_by__in=self.tenant.tenant_users.values_list('user', flat=True)
        )


class DataSourceCreateView(TenantRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Create a new data source
    """
    model = DataSource
    template_name = 'data_sources/create.html'
    fields = ['name', 'description', 'source_type', 'host', 'port', 'database_name', 
              'username', 'password', 'api_url', 'api_key', 'configuration']
    success_url = reverse_lazy('data_sources:list')
    required_permission = 'manage_settings'
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Data source created successfully!')
        return super().form_valid(form)


class DataSourceDetailView(TenantRequiredMixin, DetailView):
    """
    View data source details
    """
    model = DataSource
    template_name = 'data_sources/detail.html'
    context_object_name = 'data_source'
    
    def get_queryset(self):
        return DataSource.objects.filter(
            created_by__in=self.tenant.tenant_users.values_list('user', flat=True)
        )


class DataSourceUpdateView(TenantRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Update data source
    """
    model = DataSource
    template_name = 'data_sources/edit.html'
    fields = ['name', 'description', 'source_type', 'host', 'port', 'database_name', 
              'username', 'password', 'api_url', 'api_key', 'configuration']
    success_url = reverse_lazy('data_sources:list')
    required_permission = 'manage_settings'
    
    def get_queryset(self):
        return DataSource.objects.filter(
            created_by__in=self.tenant.tenant_users.values_list('user', flat=True)
        )
    
    def form_valid(self, form):
        messages.success(self.request, 'Data source updated successfully!')
        return super().form_valid(form)


class DataSourceDeleteView(TenantRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete data source
    """
    model = DataSource
    template_name = 'data_sources/delete.html'
    success_url = reverse_lazy('data_sources:list')
    required_permission = 'manage_settings'
    
    def get_queryset(self):
        return DataSource.objects.filter(
            created_by__in=self.tenant.tenant_users.values_list('user', flat=True)
        )
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Data source deleted successfully!')
        return super().delete(request, *args, **kwargs)


class DataSourceTestView(TenantRequiredMixin, DetailView):
    """
    Test data source connection
    """
    model = DataSource
    template_name = 'data_sources/test.html'
    
    def get_queryset(self):
        return DataSource.objects.filter(
            created_by__in=self.tenant.tenant_users.values_list('user', flat=True)
        )


class DataPullCreateView(TenantRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Create a new data pull
    """
    model = DataPull
    template_name = 'data_sources/pull_create.html'
    fields = ['query', 'parameters']
    required_permission = 'upload_data'
    
    def form_valid(self, form):
        form.instance.data_source = DataSource.objects.get(pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        messages.success(self.request, 'Data pull started successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('data_sources:pull_detail', kwargs={'pk': self.object.pk})


class DataPullDetailView(TenantRequiredMixin, DetailView):
    """
    View data pull details
    """
    model = DataPull
    template_name = 'data_sources/pull_detail.html'
    context_object_name = 'data_pull'
    
    def get_queryset(self):
        return DataPull.objects.filter(
            user__in=self.tenant.tenant_users.values_list('user', flat=True)
        )


class DataSourceTemplateListView(TenantRequiredMixin, ListView):
    """
    List data source templates
    """
    model = DataSourceTemplate
    template_name = 'data_sources/templates.html'
    context_object_name = 'templates'
    paginate_by = 20


class DataSourceTemplateDetailView(TenantRequiredMixin, DetailView):
    """
    View data source template details
    """
    model = DataSourceTemplate
    template_name = 'data_sources/template_detail.html'
    context_object_name = 'template'

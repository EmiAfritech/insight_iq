from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.db.models import Q
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import pandas as pd
from io import StringIO
import uuid

from tenants.mixins import TenantRequiredMixin
from .models import DataSet, Analysis, Chart, Insight, AnalysisTemplate
from .forms import DataSetForm, AnalysisForm, ChartForm, InsightForm, TemplateForm


# Dataset Views
class DataSetListView(TenantRequiredMixin, LoginRequiredMixin, ListView):
    """List all datasets for the current tenant."""
    model = DataSet
    template_name = 'analytics/dataset_list.html'
    context_object_name = 'datasets'
    paginate_by = 20

    def get_queryset(self):
        queryset = DataSet.objects.filter(tenant=self.request.tenant)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


class DataSetUploadView(TenantRequiredMixin, LoginRequiredMixin, CreateView):
    """Upload and create a new dataset."""
    model = DataSet
    form_class = DataSetForm
    template_name = 'analytics/dataset_upload.html'
    success_url = reverse_lazy('analytics:dataset_list')

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.uploaded_by = self.request.user
        
        # Process the uploaded file
        uploaded_file = form.cleaned_data.get('file')
        if uploaded_file:
            try:
                # Read the file based on extension
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                else:
                    messages.error(self.request, 'Unsupported file format. Please upload CSV or Excel files.')
                    return self.form_invalid(form)
                
                # Store basic metadata
                form.instance.total_rows = len(df)
                form.instance.total_columns = len(df.columns)
                form.instance.columns_info = {
                    'columns': df.columns.tolist(),
                    'dtypes': df.dtypes.astype(str).to_dict(),
                    'shape': df.shape,
                    'sample_data': df.head().to_dict('records')
                }
                form.instance.file_size = uploaded_file.size
                form.instance.file_type = uploaded_file.name.split('.')[-1].lower()
                form.instance.status = 'ready'
                
                messages.success(self.request, f'Dataset "{form.instance.name}" uploaded successfully!')
                
            except Exception as e:
                messages.error(self.request, f'Error processing file: {str(e)}')
                form.instance.status = 'error'
                form.instance.error_message = str(e)
        
        return super().form_valid(form)


class DataSetDetailView(TenantRequiredMixin, LoginRequiredMixin, DetailView):
    """View dataset details and preview data."""
    model = DataSet
    template_name = 'analytics/dataset_detail.html'
    context_object_name = 'dataset'

    def get_queryset(self):
        return DataSet.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset = self.get_object()
        
        # Get related analyses
        context['analyses'] = Analysis.objects.filter(
            dataset=dataset,
            tenant=self.request.tenant
        ).order_by('-created_at')[:5]
        
        # Get sample data if available
        if dataset.columns_info and 'sample_data' in dataset.columns_info:
            context['sample_data'] = dataset.columns_info['sample_data']
        
        return context


class DataSetUpdateView(TenantRequiredMixin, LoginRequiredMixin, UpdateView):
    """Update dataset information."""
    model = DataSet
    form_class = DataSetForm
    template_name = 'analytics/dataset_edit.html'

    def get_queryset(self):
        return DataSet.objects.filter(tenant=self.request.tenant)

    def get_success_url(self):
        return reverse_lazy('analytics:dataset_detail', kwargs={'pk': self.object.pk})


class DataSetDeleteView(TenantRequiredMixin, LoginRequiredMixin, DeleteView):
    """Delete a dataset."""
    model = DataSet
    template_name = 'analytics/dataset_delete.html'
    success_url = reverse_lazy('analytics:dataset_list')

    def get_queryset(self):
        return DataSet.objects.filter(tenant=self.request.tenant)


class DataSetPreviewView(TenantRequiredMixin, LoginRequiredMixin, DetailView):
    """Preview dataset data in a modal or separate view."""
    model = DataSet
    template_name = 'analytics/dataset_preview.html'
    context_object_name = 'dataset'

    def get_queryset(self):
        return DataSet.objects.filter(tenant=self.request.tenant)


# Analysis Views
class AnalysisCreateView(TenantRequiredMixin, LoginRequiredMixin, CreateView):
    """Create a new analysis for a dataset."""
    model = Analysis
    form_class = AnalysisForm
    template_name = 'analytics/analysis_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset_id = self.kwargs.get('dataset_id')
        if dataset_id:
            context['dataset'] = get_object_or_404(
                DataSet, 
                pk=dataset_id, 
                tenant=self.request.tenant
            )
        return context

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.created_by = self.request.user
        
        dataset_id = self.kwargs.get('dataset_id')
        if dataset_id:
            form.instance.dataset = get_object_or_404(
                DataSet, 
                pk=dataset_id, 
                tenant=self.request.tenant
            )
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('analytics:analysis_detail', kwargs={'pk': self.object.pk})


class AnalysisDetailView(TenantRequiredMixin, LoginRequiredMixin, DetailView):
    """View analysis details and results."""
    model = Analysis
    template_name = 'analytics/analysis_detail.html'
    context_object_name = 'analysis'

    def get_queryset(self):
        return Analysis.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analysis = self.get_object()
        
        # Get related charts
        context['charts'] = Chart.objects.filter(
            analysis=analysis,
            tenant=self.request.tenant
        ).order_by('-created_at')
        
        # Get related insights
        context['insights'] = Insight.objects.filter(
            analysis=analysis,
            tenant=self.request.tenant
        ).order_by('-created_at')
        
        return context


class AnalysisUpdateView(TenantRequiredMixin, LoginRequiredMixin, UpdateView):
    """Update analysis settings."""
    model = Analysis
    form_class = AnalysisForm
    template_name = 'analytics/analysis_edit.html'

    def get_queryset(self):
        return Analysis.objects.filter(tenant=self.request.tenant)

    def get_success_url(self):
        return reverse_lazy('analytics:analysis_detail', kwargs={'pk': self.object.pk})


class AnalysisDeleteView(TenantRequiredMixin, LoginRequiredMixin, DeleteView):
    """Delete an analysis."""
    model = Analysis
    template_name = 'analytics/analysis_delete.html'
    success_url = reverse_lazy('analytics:dataset_list')

    def get_queryset(self):
        return Analysis.objects.filter(tenant=self.request.tenant)


class AnalysisRunView(TenantRequiredMixin, LoginRequiredMixin, View):
    """Run/execute an analysis."""
    
    def post(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk, tenant=request.tenant)
        
        try:
            # Update analysis status
            analysis.status = 'running'
            analysis.save()
            
            # Here you would implement the actual analysis logic
            # For now, we'll just simulate success
            analysis.status = 'completed'
            analysis.save()
            
            messages.success(request, f'Analysis "{analysis.name}" completed successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Analysis completed'})
            
        except Exception as e:
            analysis.status = 'failed'
            analysis.save()
            
            messages.error(request, f'Analysis failed: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
        
        return redirect('analytics:analysis_detail', pk=pk)


class AnalysisResultsView(TenantRequiredMixin, LoginRequiredMixin, DetailView):
    """View analysis results in detail."""
    model = Analysis
    template_name = 'analytics/analysis_results.html'
    context_object_name = 'analysis'

    def get_queryset(self):
        return Analysis.objects.filter(tenant=self.request.tenant)


# Chart Views
class ChartDetailView(TenantRequiredMixin, LoginRequiredMixin, DetailView):
    """View chart details."""
    model = Chart
    template_name = 'analytics/chart_detail.html'
    context_object_name = 'chart'

    def get_queryset(self):
        return Chart.objects.filter(tenant=self.request.tenant)


class ChartUpdateView(TenantRequiredMixin, LoginRequiredMixin, UpdateView):
    """Update chart settings."""
    model = Chart
    form_class = ChartForm
    template_name = 'analytics/chart_edit.html'

    def get_queryset(self):
        return Chart.objects.filter(tenant=self.request.tenant)

    def get_success_url(self):
        return reverse_lazy('analytics:chart_detail', kwargs={'pk': self.object.pk})


class ChartDataView(TenantRequiredMixin, LoginRequiredMixin, View):
    """Return chart data as JSON for rendering."""
    
    def get(self, request, pk):
        chart = get_object_or_404(Chart, pk=pk, tenant=request.tenant)
        
        # Here you would implement chart data generation
        # For now, return mock data
        data = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'datasets': [{
                'label': chart.name,
                'data': [10, 20, 30, 40, 50],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            }]
        }
        
        return JsonResponse(data)


# Insight Views
class InsightListView(TenantRequiredMixin, LoginRequiredMixin, ListView):
    """List all insights."""
    model = Insight
    template_name = 'analytics/insight_list.html'
    context_object_name = 'insights'
    paginate_by = 20

    def get_queryset(self):
        return Insight.objects.filter(
            tenant=self.request.tenant,
            is_hidden=False
        ).order_by('-created_at')


class InsightDetailView(TenantRequiredMixin, LoginRequiredMixin, DetailView):
    """View insight details."""
    model = Insight
    template_name = 'analytics/insight_detail.html'
    context_object_name = 'insight'

    def get_queryset(self):
        return Insight.objects.filter(tenant=self.request.tenant)


class InsightVerifyView(TenantRequiredMixin, LoginRequiredMixin, View):
    """Verify an insight."""
    
    def post(self, request, pk):
        insight = get_object_or_404(Insight, pk=pk, tenant=request.tenant)
        insight.is_verified = True
        insight.verified_by = request.user
        insight.save()
        
        messages.success(request, 'Insight verified successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        return redirect('analytics:insight_detail', pk=pk)


class InsightHideView(TenantRequiredMixin, LoginRequiredMixin, View):
    """Hide an insight."""
    
    def post(self, request, pk):
        insight = get_object_or_404(Insight, pk=pk, tenant=request.tenant)
        insight.is_hidden = True
        insight.save()
        
        messages.success(request, 'Insight hidden successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        
        return redirect('analytics:insight_list')


# Template Views
class TemplateListView(TenantRequiredMixin, LoginRequiredMixin, ListView):
    """List all analysis templates."""
    model = AnalysisTemplate
    template_name = 'analytics/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

    def get_queryset(self):
        return AnalysisTemplate.objects.filter(
            Q(tenant=self.request.tenant) | Q(is_public=True)
        ).order_by('-created_at')


class TemplateDetailView(TenantRequiredMixin, LoginRequiredMixin, DetailView):
    """View template details."""
    model = AnalysisTemplate
    template_name = 'analytics/template_detail.html'
    context_object_name = 'template'

    def get_queryset(self):
        return AnalysisTemplate.objects.filter(
            Q(tenant=self.request.tenant) | Q(is_public=True)
        )


class TemplateUseView(TenantRequiredMixin, LoginRequiredMixin, View):
    """Use a template to create a new analysis."""
    
    def post(self, request, pk):
        template = get_object_or_404(
            AnalysisTemplate, 
            pk=pk
        )
        
        # Redirect to analysis creation with template
        return redirect('analytics:analysis_create')


# API Views
class DataSetColumnsAPIView(TenantRequiredMixin, LoginRequiredMixin, View):
    """API to get dataset columns."""
    
    def get(self, request, pk):
        dataset = get_object_or_404(DataSet, pk=pk, tenant=request.tenant)
        
        columns = []
        if dataset.columns_info and 'columns' in dataset.columns_info:
            columns = dataset.columns_info['columns']
        
        return JsonResponse({'columns': columns})


class AnalysisStatusAPIView(TenantRequiredMixin, LoginRequiredMixin, View):
    """API to get analysis status."""
    
    def get(self, request, pk):
        analysis = get_object_or_404(Analysis, pk=pk, tenant=request.tenant)
        
        return JsonResponse({
            'status': analysis.status,
            'progress': getattr(analysis, 'progress', 0),
            'message': getattr(analysis, 'status_message', '')
        })


class ChartExportAPIView(TenantRequiredMixin, LoginRequiredMixin, View):
    """API to export chart data."""
    
    def get(self, request, pk):
        chart = get_object_or_404(Chart, pk=pk, tenant=request.tenant)
        
        # Here you would implement chart export logic
        # For now, return success
        return JsonResponse({'status': 'success', 'url': '/path/to/exported/chart'})

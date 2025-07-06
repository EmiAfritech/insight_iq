from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from tenants.decorators import tenant_required
from tenants.mixins import TenantRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import (
    Report, ReportTemplate, ReportSection, 
    ReportShare, ReportComment, ReportExport
)
from .forms import ReportForm, ReportTemplateForm, ReportShareForm, ReportCommentForm
from .utils import generate_report, export_report
import json
import os


class ReportListView(LoginRequiredMixin, TenantRequiredMixin, ListView):
    """List all reports for the current tenant"""
    model = Report
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Report.objects.filter(tenant=self.request.tenant)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(executive_summary__icontains=search_query)
            )
        
        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by format
        format_filter = self.request.GET.get('format')
        if format_filter:
            queryset = queryset.filter(format=format_filter)
        
        return queryset.select_related('created_by', 'template').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_choices'] = Report.STATUS_CHOICES
        context['format_choices'] = Report.FORMAT_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        context['current_format'] = self.request.GET.get('format', '')
        return context


class ReportDetailView(LoginRequiredMixin, TenantRequiredMixin, DetailView):
    """View a specific report"""
    model = Report
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'
    pk_url_kwarg = 'report_id'
    
    def get_queryset(self):
        return Report.objects.filter(tenant=self.request.tenant)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.get_object()
        
        # Get report sections
        context['sections'] = report.sections.filter(is_visible=True).order_by('order')
        
        # Get comments
        context['comments'] = report.comments.filter(parent=None).order_by('-created_at')
        context['comment_form'] = ReportCommentForm()
        
        # Get sharing info
        context['shares'] = report.shares.all().order_by('-created_at')
        context['share_form'] = ReportShareForm()
        
        # Check if user can edit
        context['can_edit'] = (
            report.created_by == self.request.user or 
            self.request.user.has_perm('reports.change_report')
        )
        
        return context


class ReportCreateView(LoginRequiredMixin, TenantRequiredMixin, CreateView):
    """Create a new report"""
    model = Report
    form_class = ReportForm
    template_name = 'reports/report_create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs
    
    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Generate report if requested
        if form.cleaned_data.get('generate_now'):
            generate_report.delay(self.object.id)
            messages.success(self.request, 'Report created and generation started!')
        else:
            messages.success(self.request, 'Report created successfully!')
        
        return response


class ReportUpdateView(LoginRequiredMixin, TenantRequiredMixin, UpdateView):
    """Edit an existing report"""
    model = Report
    form_class = ReportForm
    template_name = 'reports/report_edit.html'
    pk_url_kwarg = 'report_id'
    
    def get_queryset(self):
        return Report.objects.filter(tenant=self.request.tenant)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Regenerate report if requested
        if form.cleaned_data.get('regenerate'):
            generate_report.delay(self.object.id)
            messages.success(self.request, 'Report updated and regeneration started!')
        else:
            messages.success(self.request, 'Report updated successfully!')
        
        return response


class ReportDeleteView(TenantRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Delete report
    """
    template_name = 'reports/delete.html'
    success_url = reverse_lazy('reports:list')
    required_permission = 'create_reports'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Report deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ReportExportView(TenantRequiredMixin, TemplateView):
    """
    Export report
    """
    template_name = 'reports/export.html'


class ReportShareView(TenantRequiredMixin, TemplateView):
    """
    Share report
    """
    template_name = 'reports/share.html'


class ReportTemplateListView(TenantRequiredMixin, ListView):
    """
    List report templates
    """
    template_name = 'reports/templates.html'
    context_object_name = 'templates'
    paginate_by = 20
    
    def get_queryset(self):
        # Placeholder - implement with actual ReportTemplate model
        return []


@login_required
@tenant_required
def report_export(request, report_id):
    """Export a report in various formats"""
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    if request.method == 'POST':
        export_format = request.POST.get('format', 'pdf')
        
        # Create export record
        export_record = ReportExport.objects.create(
            report=report,
            exported_by=request.user,
            format=export_format
        )
        
        try:
            # Generate export file
            file_path = export_report(report, export_format)
            export_record.file_path = file_path
            
            # Get file size
            if os.path.exists(file_path):
                export_record.file_size = os.path.getsize(file_path)
            
            export_record.save()
            
            # Return file for download
            with open(file_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{report.title}.{export_format}"'
                return response
                
        except Exception as e:
            messages.error(request, f'Error exporting report: {str(e)}')
            return redirect('reports:report_detail', report_id=report.id)
    
    return render(request, 'reports/report_export.html', {'report': report})


@login_required
@tenant_required
def report_share(request, report_id):
    """Share a report with others"""
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    if request.method == 'POST':
        form = ReportShareForm(request.POST)
        if form.is_valid():
            share = form.save(commit=False)
            share.report = report
            share.shared_by = request.user
            share.save()
            
            # TODO: Send email notification
            messages.success(request, f'Report shared with {share.shared_with_email}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Report shared successfully'
                })
            
            return redirect('reports:report_detail', report_id=report.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
@tenant_required
def report_comment(request, report_id):
    """Add a comment to a report"""
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    if request.method == 'POST':
        form = ReportCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.report = report
            comment.author = request.user
            
            # Handle replies
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(ReportComment, id=parent_id, report=report)
                comment.parent = parent_comment
            
            comment.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'author': comment.author.username,
                        'created_at': comment.created_at.isoformat()
                    }
                })
            
            messages.success(request, 'Comment added successfully!')
            return redirect('reports:report_detail', report_id=report.id)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
@tenant_required
def report_generate(request, report_id):
    """Generate/regenerate a report"""
    report = get_object_or_404(Report, id=report_id, tenant=request.tenant)
    
    if request.method == 'POST':
        # Update status
        report.status = 'generating'
        report.save()
        
        # Start generation task
        generate_report.delay(report.id)
        
        messages.success(request, 'Report generation started!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Report generation started'
            })
        
        return redirect('reports:report_detail', report_id=report.id)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
@tenant_required
def report_template_list(request):
    """List report templates"""
    templates = ReportTemplate.objects.filter(
        tenant=request.tenant,
        is_active=True
    ).order_by('name')
    
    return render(request, 'reports/template_list.html', {
        'templates': templates
    })


@login_required
@tenant_required
def report_template_create(request):
    """Create a new report template"""
    if request.method == 'POST':
        form = ReportTemplateForm(request.POST, tenant=request.tenant)
        if form.is_valid():
            template = form.save(commit=False)
            template.tenant = request.tenant
            template.created_by = request.user
            template.save()
            
            messages.success(request, 'Report template created successfully!')
            return redirect('reports:template_list')
    else:
        form = ReportTemplateForm(tenant=request.tenant)
    
    return render(request, 'reports/template_create.html', {'form': form})


def public_report_view(request, share_token):
    """View a publicly shared report"""
    report = get_object_or_404(Report, share_token=share_token)
    
    if not report.is_public:
        raise Http404("Report not found or not public")
    
    # Track the view
    share = ReportShare.objects.filter(report=report).first()
    if share:
        share.access_count += 1
        share.accessed_at = timezone.now()
        share.save()
    
    return render(request, 'reports/public_report.html', {
        'report': report,
        'sections': report.sections.filter(is_visible=True).order_by('order')
    })


# Function-based views for backwards compatibility
report_list = ReportListView.as_view()
report_detail = ReportDetailView.as_view()
report_create = ReportCreateView.as_view()
report_edit = ReportUpdateView.as_view()

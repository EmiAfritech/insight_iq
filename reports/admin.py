from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    ReportTemplate, Report, ReportSection, 
    ReportShare, ReportComment, ReportExport
)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'tenant', 'is_active', 'created_by', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at', 'tenant']
    search_fields = ['name', 'description', 'tenant__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'template_type', 'tenant', 'is_active')
        }),
        ('Template Data', {
            'fields': ('template_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tenant', 'created_by')


class ReportSectionInline(admin.TabularInline):
    model = ReportSection
    extra = 0
    fields = ['title', 'section_type', 'order', 'is_visible']
    ordering = ['order']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'tenant', 'status', 'format', 'created_by', 
        'is_scheduled', 'generated_at', 'created_at'
    ]
    list_filter = [
        'status', 'format', 'is_scheduled', 'schedule_frequency', 
        'is_public', 'created_at', 'tenant'
    ]
    search_fields = ['title', 'description', 'tenant__name', 'created_by__username']
    readonly_fields = ['id', 'share_token', 'created_at', 'updated_at', 'file_size']
    inlines = [ReportSectionInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'tenant', 'template', 'status')
        }),
        ('Content', {
            'fields': ('executive_summary', 'key_insights', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Data Sources', {
            'fields': ('dashboards', 'analyses'),
            'classes': ('collapse',)
        }),
        ('Generation Settings', {
            'fields': (
                'format', 'include_charts', 'include_data_tables', 
                'include_appendix'
            ),
            'classes': ('collapse',)
        }),
        ('Scheduling', {
            'fields': (
                'is_scheduled', 'schedule_frequency', 'next_generation'
            ),
            'classes': ('collapse',)
        }),
        ('Sharing & Access', {
            'fields': ('is_public', 'share_token'),
            'classes': ('collapse',)
        }),
        ('File Info', {
            'fields': ('file_path', 'file_size', 'generated_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['dashboards', 'analyses']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'tenant', 'template', 'created_by'
        ).prefetch_related('dashboards', 'analyses')


@admin.register(ReportSection)
class ReportSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'report', 'section_type', 'order', 'is_visible']
    list_filter = ['section_type', 'is_visible', 'report__tenant']
    search_fields = ['title', 'report__title', 'report__tenant__name']
    list_editable = ['order', 'is_visible']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('report', 'report__tenant')


@admin.register(ReportShare)
class ReportShareAdmin(admin.ModelAdmin):
    list_display = [
        'report', 'shared_with_email', 'access_level', 'access_count', 
        'expires_at', 'is_expired_display', 'created_at'
    ]
    list_filter = ['access_level', 'expires_at', 'created_at']
    search_fields = ['report__title', 'shared_with_email', 'shared_by__username']
    readonly_fields = ['accessed_at', 'access_count', 'created_at']
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired_display.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'report', 'report__tenant', 'shared_by'
        )


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = [
        'report', 'author', 'content_preview', 'section', 
        'is_resolved', 'created_at'
    ]
    list_filter = ['is_resolved', 'created_at', 'report__tenant']
    search_fields = ['content', 'report__title', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'report', 'report__tenant', 'author', 'section'
        )


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = [
        'report', 'exported_by', 'format', 'file_size_display', 'created_at'
    ]
    list_filter = ['format', 'created_at']
    search_fields = ['report__title', 'exported_by__username']
    readonly_fields = ['created_at', 'file_size']
    
    def file_size_display(self, obj):
        if obj.file_size:
            # Convert bytes to MB
            size_mb = obj.file_size / (1024 * 1024)
            return f"{size_mb:.2f} MB"
        return "-"
    file_size_display.short_description = 'File Size'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'report', 'report__tenant', 'exported_by'
        )

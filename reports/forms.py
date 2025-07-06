from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    Report, ReportTemplate, ReportSection, 
    ReportShare, ReportComment, ReportExport
)
from dashboards.models import Dashboard
from analytics.models import Analysis

User = get_user_model()


class ReportForm(forms.ModelForm):
    """Form for creating and editing reports"""
    
    generate_now = forms.BooleanField(
        required=False,
        label="Generate report immediately",
        help_text="Check this to start generating the report right after creation"
    )
    
    regenerate = forms.BooleanField(
        required=False,
        label="Regenerate report",
        help_text="Check this to regenerate the report after updating"
    )
    
    class Meta:
        model = Report
        fields = [
            'title', 'description', 'template', 'dashboards', 'analyses',
            'format', 'include_charts', 'include_data_tables', 'include_appendix',
            'is_scheduled', 'schedule_frequency', 'next_generation',
            'executive_summary', 'recommendations', 'is_public'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter report title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter report description'
            }),
            'template': forms.Select(attrs={'class': 'form-control'}),
            'dashboards': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'analyses': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'schedule_frequency': forms.Select(attrs={'class': 'form-control'}),
            'next_generation': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'executive_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter executive summary'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter recommendations'
            }),
            'include_charts': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_data_tables': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_appendix': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_scheduled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        if self.tenant:
            # Filter templates by tenant
            self.fields['template'].queryset = ReportTemplate.objects.filter(
                tenant=self.tenant,
                is_active=True
            )
            
            # Filter dashboards by tenant
            self.fields['dashboards'].queryset = Dashboard.objects.filter(
                tenant=self.tenant
            )
            
            # Filter analyses by tenant
            self.fields['analyses'].queryset = Analysis.objects.filter(
                tenant=self.tenant
            )
    
    def clean_next_generation(self):
        next_generation = self.cleaned_data.get('next_generation')
        is_scheduled = self.cleaned_data.get('is_scheduled')
        
        if is_scheduled and not next_generation:
            raise forms.ValidationError("Next generation time is required for scheduled reports")
        
        if next_generation and next_generation <= timezone.now():
            raise forms.ValidationError("Next generation time must be in the future")
        
        return next_generation
    
    def clean(self):
        cleaned_data = super().clean()
        dashboards = cleaned_data.get('dashboards')
        analyses = cleaned_data.get('analyses')
        
        if not dashboards and not analyses:
            raise forms.ValidationError("At least one dashboard or analysis must be selected")
        
        return cleaned_data


class ReportTemplateForm(forms.ModelForm):
    """Form for creating and editing report templates"""
    
    class Meta:
        model = ReportTemplate
        fields = [
            'name', 'description', 'template_type', 'template_data', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter template name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter template description'
            }),
            'template_type': forms.Select(attrs={'class': 'form-control'}),
            'template_data': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Enter template configuration (JSON format)'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
    
    def clean_template_data(self):
        template_data = self.cleaned_data.get('template_data')
        
        if template_data:
            try:
                import json
                json.loads(template_data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Template data must be valid JSON")
        
        return template_data


class ReportSectionForm(forms.ModelForm):
    """Form for creating and editing report sections"""
    
    class Meta:
        model = ReportSection
        fields = [
            'title', 'section_type', 'content', 'order', 'is_visible'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section title'
            }),
            'section_type': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter section content (JSON format)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        
        if content:
            try:
                import json
                json.loads(content)
            except json.JSONDecodeError:
                raise forms.ValidationError("Content must be valid JSON")
        
        return content


class ReportShareForm(forms.ModelForm):
    """Form for sharing reports"""
    
    class Meta:
        model = ReportShare
        fields = [
            'shared_with_email', 'message', 'access_level', 'expires_at'
        ]
        widgets = {
            'shared_with_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter optional message'
            }),
            'access_level': forms.Select(attrs={'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def clean_expires_at(self):
        expires_at = self.cleaned_data.get('expires_at')
        
        if expires_at and expires_at <= timezone.now():
            raise forms.ValidationError("Expiration time must be in the future")
        
        return expires_at


class ReportCommentForm(forms.ModelForm):
    """Form for adding comments to reports"""
    
    class Meta:
        model = ReportComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your comment'
            }),
        }


class ReportExportForm(forms.Form):
    """Form for exporting reports"""
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('powerpoint', 'PowerPoint'),
    ]
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    include_charts = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_data_tables = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    include_appendix = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class ReportSearchForm(forms.Form):
    """Form for searching reports"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search reports...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Report.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    format = forms.ChoiceField(
        required=False,
        choices=[('', 'All Formats')] + Report.FORMAT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Start date must be before end date")
        
        return cleaned_data

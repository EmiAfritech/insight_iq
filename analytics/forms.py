from django import forms
from django.core.exceptions import ValidationError
from .models import DataSet, Analysis, Chart, Insight, AnalysisTemplate


class DataSetForm(forms.ModelForm):
    """Form for creating and editing datasets."""
    
    file = forms.FileField(
        required=False,
        help_text="Upload a CSV or Excel file",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    
    class Meta:
        model = DataSet
        fields = ['name', 'description', 'file', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter dataset name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your dataset'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (limit to 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 10MB.')
            
            # Check file extension
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise ValidationError('Only CSV and Excel files are allowed.')
        
        return file


class AnalysisForm(forms.ModelForm):
    """Form for creating and editing analyses."""
    
    class Meta:
        model = Analysis
        fields = ['name', 'description', 'analysis_type', 'configuration', 'selected_columns']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter analysis name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your analysis'
            }),
            'analysis_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'configuration': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter analysis configuration as JSON'
            }),
            'selected_columns': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter selected columns as JSON array'
            })
        }
    
    def clean_configuration(self):
        configuration = self.cleaned_data.get('configuration')
        if configuration:
            try:
                import json
                json.loads(configuration)
            except json.JSONDecodeError:
                raise ValidationError('Configuration must be valid JSON.')
        return configuration
    
    def clean_selected_columns(self):
        selected_columns = self.cleaned_data.get('selected_columns')
        if selected_columns:
            try:
                import json
                data = json.loads(selected_columns)
                if not isinstance(data, list):
                    raise ValidationError('Selected columns must be a JSON array.')
            except json.JSONDecodeError:
                raise ValidationError('Selected columns must be valid JSON.')
        return selected_columns


class ChartForm(forms.ModelForm):
    """Form for creating and editing charts."""
    
    class Meta:
        model = Chart
        fields = ['name', 'description', 'chart_type', 'configuration']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter chart name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your chart'
            }),
            'chart_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'configuration': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter chart configuration as JSON'
            })
        }
    
    def clean_configuration(self):
        configuration = self.cleaned_data.get('configuration')
        if configuration:
            try:
                import json
                json.loads(configuration)
            except json.JSONDecodeError:
                raise ValidationError('Configuration must be valid JSON.')
        return configuration


class InsightForm(forms.ModelForm):
    """Form for creating and editing insights."""
    
    class Meta:
        model = Insight
        fields = ['title', 'description', 'insight_type', 'confidence_score']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter insight title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the insight'
            }),
            'insight_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'confidence_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
                'step': 1
            })
        }


class TemplateForm(forms.ModelForm):
    """Form for creating and editing analysis templates."""
    
    class Meta:
        model = AnalysisTemplate
        fields = ['name', 'description', 'analysis_type', 'configuration', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter template name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the template'
            }),
            'analysis_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'configuration': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter template configuration as JSON'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_configuration(self):
        configuration = self.cleaned_data.get('configuration')
        if configuration:
            try:
                import json
                json.loads(configuration)
            except json.JSONDecodeError:
                raise ValidationError('Configuration must be valid JSON.')
        return configuration


class DataUploadForm(forms.Form):
    """Simplified form for data upload."""
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx,.xls'
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (limit to 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 10MB.')
            
            # Check file extension
            allowed_extensions = ['.csv', '.xlsx', '.xls']
            if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                raise ValidationError('Only CSV and Excel files are allowed.')
        
        return file


class AnalysisFilterForm(forms.Form):
    """Form for filtering analyses."""
    
    ANALYSIS_TYPE_CHOICES = [
        ('', 'All Types'),
        ('descriptive', 'Descriptive'),
        ('predictive', 'Predictive'),
        ('diagnostic', 'Diagnostic'),
        ('prescriptive', 'Prescriptive'),
    ]
    
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search analyses...'
        })
    )
    
    analysis_type = forms.ChoiceField(
        choices=ANALYSIS_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
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

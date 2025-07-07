import re
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import Tenant, TenantUser, Domain


class SimpleTenantCreationForm(forms.ModelForm):
    """
    Simplified form for creating a new tenant - collects basic info only
    """
    domain_name = forms.CharField(
        max_length=50,
        label="Organization URL",
        help_text="This will be used as your subdomain (e.g., yourcompany.insightiq.com)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'yourcompany'
        })
    )
    
    class Meta:
        """Meta configuration for SimpleTenantCreationForm"""
        model = Tenant
        fields = ['name', 'company_description', 'company_logo', 'contact_email']
        labels = {
            'name': 'Organization Name',
            'company_description': 'Description',
            'company_logo': 'Organization Logo',
            'contact_email': 'Contact Email'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your organization name'
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of your organization (optional)'
            }),
            'company_logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@yourcompany.com'
            })
        }
    
    def clean_domain_name(self):
        """Validate and clean the domain name"""
        domain_name = self.cleaned_data['domain_name']
        # Remove spaces and convert to lowercase
        domain_name = domain_name.lower().replace(' ', '-').replace('_', '-')
        # Remove special characters
        domain_name = re.sub(r'[^a-z0-9-]', '', domain_name)
        # Remove multiple consecutive dashes
        domain_name = re.sub(r'-+', '-', domain_name).strip('-')
        
        if not domain_name:
            raise forms.ValidationError("Please enter a valid organization URL.")
        
        # Check if domain already exists
        tenant_domain = getattr(settings, 'TENANT_DOMAIN', 'localhost')
        full_domain = f"{domain_name}.{tenant_domain}"
        if Domain.objects.filter(domain=full_domain).exists():
            raise forms.ValidationError(
                "This organization URL is already taken. Please choose another."
            )
            
        # Check if the generated schema name would be unique
        schema_name = re.sub(r'[^a-z0-9_]', '', domain_name.lower())
        if not schema_name or not schema_name[0].isalpha():
            schema_name = 'tenant_' + (schema_name or 'org')
        
        # Check if schema already exists
        if Tenant.objects.filter(schema_name=schema_name[:63]).exists():
            raise forms.ValidationError(
                "This organization URL would create a duplicate schema. Please choose another."
            )
            
        return domain_name
    
    def save(self, commit=True):
        """Save the tenant instance"""
        tenant = super().save(commit=False)
        
        # Set company_name to name if not provided
        if not tenant.company_name:
            tenant.company_name = tenant.name
            
        # Generate schema_name from domain_name if not set
        if not tenant.schema_name:
            domain_name = self.cleaned_data.get('domain_name', '')
            if domain_name:
                # Use domain name as schema name (cleaned)
                schema_name = re.sub(r'[^a-z0-9_]', '', domain_name.lower())
                if not schema_name:
                    schema_name = re.sub(r'[^a-z0-9_]', '', tenant.name.lower())
                
                # Ensure it starts with a letter (PostgreSQL requirement)
                if schema_name and not schema_name[0].isalpha():
                    schema_name = 'tenant_' + schema_name
                
                # Ensure it's not empty and not too long
                if not schema_name:
                    schema_name = 'tenant_' + str(hash(tenant.name))[:8]
                
                tenant.schema_name = schema_name[:63]  # PostgreSQL limit
        
        if commit:
            tenant.save()
        return tenant


class TenantCreationForm(forms.ModelForm):
    """
    Full form for creating a new tenant with all details
    """
    domain_name = forms.CharField(
        max_length=50,
        help_text="This will be used as your subdomain (e.g., yourcompany.insightiq.com)"
    )
    
    class Meta:
        model = Tenant
        fields = [
            'name', 'company_name', 'company_description', 'company_website',
            'contact_email', 'contact_phone', 'address_line1', 'address_line2',
            'city', 'state', 'country', 'postal_code'
        ]
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('domain_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('company_name', css_class='form-group col-md-6 mb-0'),
                Column('company_website', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'company_description',
            Row(
                Column('contact_email', css_class='form-group col-md-6 mb-0'),
                Column('contact_phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('address_line1', css_class='form-group col-md-6 mb-0'),
                Column('address_line2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('city', css_class='form-group col-md-4 mb-0'),
                Column('state', css_class='form-group col-md-4 mb-0'),
                Column('postal_code', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'country',
            Submit('submit', 'Create Tenant', css_class='btn btn-primary')
        )
    
    def clean_domain_name(self):
        """Validate and clean the domain name"""
        domain_name = self.cleaned_data['domain_name']
        # Remove spaces and convert to lowercase
        domain_name = domain_name.lower().replace(' ', '-')
        # Check if domain already exists
        if Domain.objects.filter(domain__icontains=domain_name).exists():
            raise forms.ValidationError("This domain name is already taken.")
        return domain_name


class TenantSettingsForm(forms.ModelForm):
    """
    Form for updating tenant settings
    """
    class Meta:
        model = Tenant
        fields = [
            'company_name', 'company_description', 'company_logo', 'company_website',
            'contact_email', 'contact_phone', 'address_line1', 'address_line2',
            'city', 'state', 'country', 'postal_code'
        ]
        widgets = {
            'company_description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('company_name', css_class='form-group col-md-6 mb-0'),
                Column('company_website', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'company_description',
            'company_logo',
            Row(
                Column('contact_email', css_class='form-group col-md-6 mb-0'),
                Column('contact_phone', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('address_line1', css_class='form-group col-md-6 mb-0'),
                Column('address_line2', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('city', css_class='form-group col-md-4 mb-0'),
                Column('state', css_class='form-group col-md-4 mb-0'),
                Column('postal_code', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            'country',
            Submit('submit', 'Update Settings', css_class='btn btn-primary')
        )


class TenantUserForm(forms.ModelForm):
    """
    Form for editing tenant user
    """
    class Meta:
        model = TenantUser
        fields = [
            'role', 'phone', 'department', 'job_title', 'profile_picture',
            'can_upload_data', 'can_create_reports', 'can_view_all_data',
            'can_manage_users', 'can_manage_settings', 'is_active'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('role', css_class='form-group col-md-6 mb-0'),
                Column('is_active', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('phone', css_class='form-group col-md-6 mb-0'),
                Column('department', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('job_title', css_class='form-group col-md-6 mb-0'),
                Column('profile_picture', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('can_upload_data'),
            Field('can_create_reports'),
            Field('can_view_all_data'),
            Field('can_manage_users'),
            Field('can_manage_settings'),
            Submit('submit', 'Update User', css_class='btn btn-primary')
        )


class UserInviteForm(forms.Form):
    """
    Form for inviting new users to tenant
    """
    email = forms.EmailField(
        label="Email Address",
        help_text="Enter the email address of the person you want to invite"
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="Optional: First name of the person"
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text="Optional: Last name of the person"
    )
    role = forms.ChoiceField(
        choices=TenantUser.ROLE_CHOICES,
        initial='analyst',
        help_text="Select the role for this user"
    )
    
    def __init__(self, *args, **kwargs):
        # Remove instance if passed (UserInviteForm is not a ModelForm)
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-0'),
                Column('last_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'role',
            Submit('submit', 'Send Invitation', css_class='btn btn-primary')
        )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # Additional validation can be added here
        return email

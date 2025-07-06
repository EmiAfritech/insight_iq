from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Contact form for public and tenant pages
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'email',
            'subject',
            'message',
            Submit('submit', 'Send Message', css_class='btn btn-primary')
        )
        
        # Add CSS classes
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
    
    def clean_message(self):
        message = self.cleaned_data['message']
        if len(message) < 10:
            raise forms.ValidationError("Message must be at least 10 characters long.")
        return message

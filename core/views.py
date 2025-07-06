from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ContactForm
from .models import ContactMessage


class PublicLandingView(TemplateView):
    """
    Public landing page for the SaaS
    """
    template_name = 'core/public_landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'features': [
                {
                    'title': 'AI-Powered Analysis',
                    'description': 'Automated data analysis with machine learning insights',
                    'icon': 'fas fa-robot'
                },
                {
                    'title': 'Interactive Dashboards',
                    'description': 'Beautiful, responsive dashboards with real-time data',
                    'icon': 'fas fa-chart-line'
                },
                {
                    'title': 'Multi-Source Data',
                    'description': 'Connect multiple data sources and databases',
                    'icon': 'fas fa-database'
                },
                {
                    'title': 'Professional Reports',
                    'description': 'Generate executive-ready reports in minutes',
                    'icon': 'fas fa-file-alt'
                }
            ],
            'testimonials': [
                {
                    'name': 'John Smith',
                    'company': 'Tech Corp',
                    'message': 'InsightIQ transformed how we analyze our business data.',
                    'rating': 5
                },
                {
                    'name': 'Sarah Johnson',
                    'company': 'Analytics Inc',
                    'message': 'The AI insights saved us hours of manual analysis.',
                    'rating': 5
                }
            ]
        })
        return context


class PublicFeaturesView(TemplateView):
    """
    Public features page
    """
    template_name = 'core/public_features.html'


class PublicPricingView(TemplateView):
    """
    Public pricing page
    """
    template_name = 'core/public_pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pricing_plans'] = [
            {
                'name': 'Starter',
                'price': 29,
                'features': [
                    '5 Users',
                    '10GB Storage',
                    'Basic Analytics',
                    'Email Support'
                ],
                'recommended': False
            },
            {
                'name': 'Professional',
                'price': 99,
                'features': [
                    '25 Users',
                    '100GB Storage',
                    'AI-Powered Insights',
                    'Advanced Analytics',
                    'Priority Support'
                ],
                'recommended': True
            },
            {
                'name': 'Enterprise',
                'price': 299,
                'features': [
                    'Unlimited Users',
                    '1TB Storage',
                    'Custom Integrations',
                    'White-label Solution',
                    'Dedicated Support'
                ],
                'recommended': False
            }
        ]
        return context


class PublicAboutView(TemplateView):
    """
    Public about page
    """
    template_name = 'core/public_about.html'


class PublicContactView(FormView):
    """
    Public contact page
    """
    template_name = 'core/public_contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:public_contact')
    
    def form_valid(self, form):
        contact_message = ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )
        messages.success(self.request, 'Thank you for your message! We will get back to you soon.')
        return super().form_valid(form)


class DemoView(TemplateView):
    """
    Demo page showing sample dashboards
    """
    template_name = 'core/demo.html'


class PrivacyView(TemplateView):
    """
    Privacy policy page
    """
    template_name = 'core/privacy.html'


class TermsView(TemplateView):
    """
    Terms of service page
    """
    template_name = 'core/terms.html'


# Tenant-specific views
class LandingView(LoginRequiredMixin, TemplateView):
    """
    Tenant landing page (after login)
    """
    template_name = 'core/landing.html'


class FeaturesView(LoginRequiredMixin, TemplateView):
    """
    Tenant features page
    """
    template_name = 'core/features.html'


class PricingView(LoginRequiredMixin, TemplateView):
    """
    Tenant pricing page
    """
    template_name = 'core/pricing.html'


class AboutView(LoginRequiredMixin, TemplateView):
    """
    Tenant about page
    """
    template_name = 'core/about.html'


class ContactView(LoginRequiredMixin, FormView):
    """
    Tenant contact page
    """
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contact')
    
    def form_valid(self, form):
        contact_message = ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message'],
            user=self.request.user if self.request.user.is_authenticated else None
        )
        messages.success(self.request, 'Thank you for your message! We will get back to you soon.')
        return super().form_valid(form)

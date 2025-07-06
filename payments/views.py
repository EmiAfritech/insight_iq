from django.shortcuts import render
from django.views.generic import ListView, CreateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from tenants.mixins import TenantRequiredMixin, PermissionRequiredMixin
from .models import Payment, PaymentMethod, Invoice, Refund


class PaymentListView(TenantRequiredMixin, ListView):
    """
    List all payments for the tenant
    """
    model = Payment
    template_name = 'payments/list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        return Payment.objects.filter(tenant=self.tenant).order_by('-created_at')


class PaymentMethodListView(TenantRequiredMixin, LoginRequiredMixin, ListView):
    """
    List payment methods for the tenant
    """
    model = PaymentMethod
    template_name = 'payments/methods.html'
    context_object_name = 'payment_methods'
    required_permission = 'manage_settings'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(tenant=self.tenant, is_active=True)


class PaymentMethodCreateView(TenantRequiredMixin, LoginRequiredMixin, CreateView):
    """
    Add a new payment method
    """
    model = PaymentMethod
    template_name = 'payments/add_method.html'
    fields = ['type', 'brand', 'last_four_digits']
    success_url = reverse_lazy('payments:methods')
    required_permission = 'manage_settings'
    
    def form_valid(self, form):
        form.instance.tenant = self.tenant
        messages.success(self.request, 'Payment method added successfully!')
        return super().form_valid(form)


class PaymentMethodDeleteView(TenantRequiredMixin, LoginRequiredMixin, DeleteView):
    """
    Delete a payment method
    """
    model = PaymentMethod
    template_name = 'payments/delete_method.html'
    success_url = reverse_lazy('payments:methods')
    required_permission = 'manage_settings'
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(tenant=self.tenant)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Payment method deleted successfully!')
        return super().delete(request, *args, **kwargs)


class InvoiceListView(TenantRequiredMixin, ListView):
    """
    List invoices for the tenant
    """
    model = Invoice
    template_name = 'payments/invoices.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        return Invoice.objects.filter(tenant=self.tenant).order_by('-issued_at')


class InvoiceDetailView(TenantRequiredMixin, DetailView):
    """
    View invoice details
    """
    model = Invoice
    template_name = 'payments/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return Invoice.objects.filter(tenant=self.tenant)


class CheckoutView(TenantRequiredMixin, TemplateView):
    """
    Checkout page for payments
    """
    template_name = 'payments/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add Stripe public key and other checkout data
        from django.conf import settings
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        return context


class PaymentSuccessView(TenantRequiredMixin, TemplateView):
    """
    Payment success page
    """
    template_name = 'payments/success.html'


class PaymentCancelView(TenantRequiredMixin, TemplateView):
    """
    Payment cancel page
    """
    template_name = 'payments/cancel.html'


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(TemplateView):
    """
    Stripe webhook handler
    """
    def post(self, request, *args, **kwargs):
        import stripe
        from django.conf import settings
        
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            # Handle successful payment
            pass
        elif event['type'] == 'payment_intent.payment_failed':
            # Handle failed payment
            pass
        elif event['type'] == 'invoice.payment_succeeded':
            # Handle successful invoice payment
            pass
        elif event['type'] == 'customer.subscription.updated':
            # Handle subscription updates
            pass
        elif event['type'] == 'customer.subscription.deleted':
            # Handle subscription cancellation
            pass
        
        return HttpResponse(status=200)

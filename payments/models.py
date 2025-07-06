from django.db import models
from django.contrib.auth.models import User
from tenants.models import Tenant
from subscriptions.models import Subscription
import uuid


class Payment(models.Model):
    """
    Model for payment records
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Payment status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe integration
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True)
    
    # Payment method
    payment_method = models.CharField(max_length=50, blank=True)
    last_four_digits = models.CharField(max_length=4, blank=True)
    
    # Metadata
    description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'payments_payment'
    
    def __str__(self):
        return f"{self.tenant.name} - ${self.amount} - {self.status}"


class Invoice(models.Model):
    """
    Model for invoices
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invoices')
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='invoices')
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True)
    
    # Invoice details
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Billing period
    billing_start = models.DateField()
    billing_end = models.DateField()
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('void', 'Void'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Stripe integration
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    
    # Files
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    class Meta:
        ordering = ['-issued_at']
        db_table = 'payments_invoice'
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.tenant.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)


class PaymentMethod(models.Model):
    """
    Model for stored payment methods
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payment_methods')
    
    # Payment method details
    TYPE_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank_account', 'Bank Account'),
        ('paypal', 'PayPal'),
        ('other', 'Other'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Card details
    brand = models.CharField(max_length=20, blank=True)
    last_four_digits = models.CharField(max_length=4, blank=True)
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    
    # Stripe integration
    stripe_payment_method_id = models.CharField(max_length=100, blank=True)
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments_paymentmethod'
    
    def __str__(self):
        return f"{self.tenant.name} - {self.brand} ****{self.last_four_digits}"


class Refund(models.Model):
    """
    Model for refunds
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe integration
    stripe_refund_id = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'payments_refund'
    
    def __str__(self):
        return f"Refund ${self.amount} - {self.payment.tenant.name}"

from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='list'),
    path('methods/', views.PaymentMethodListView.as_view(), name='methods'),
    path('methods/add/', views.PaymentMethodCreateView.as_view(), name='add_method'),
    path('methods/<uuid:pk>/delete/', views.PaymentMethodDeleteView.as_view(), name='delete_method'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    path('invoices/<uuid:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='cancel'),
    path('webhook/', views.StripeWebhookView.as_view(), name='webhook'),
]

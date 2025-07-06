from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Public URLs
    path('', views.PublicLandingView.as_view(), name='public_landing'),
    path('features/', views.PublicFeaturesView.as_view(), name='public_features'),
    path('pricing/', views.PublicPricingView.as_view(), name='public_pricing'),
    path('about/', views.PublicAboutView.as_view(), name='public_about'),
    path('contact/', views.PublicContactView.as_view(), name='public_contact'),
    path('demo/', views.DemoView.as_view(), name='demo'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    
    # Authenticated URLs
    path('dashboard/', views.LandingView.as_view(), name='landing'),
    path('dashboard/features/', views.FeaturesView.as_view(), name='features'),
    path('dashboard/pricing/', views.PricingView.as_view(), name='pricing'),
    path('dashboard/about/', views.AboutView.as_view(), name='about'),
    path('dashboard/contact/', views.ContactView.as_view(), name='contact'),
]

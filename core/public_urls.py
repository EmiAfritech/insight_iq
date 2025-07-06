from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PublicLandingView.as_view(), name='public_landing'),
    path('features/', views.PublicFeaturesView.as_view(), name='public_features'),
    path('pricing/', views.PublicPricingView.as_view(), name='public_pricing'),
    path('about/', views.PublicAboutView.as_view(), name='public_about'),
    path('contact/', views.PublicContactView.as_view(), name='public_contact'),
    path('privacy/', views.PrivacyView.as_view(), name='privacy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('demo/', views.DemoView.as_view(), name='demo'),
]

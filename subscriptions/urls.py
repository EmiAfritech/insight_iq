from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscriptionPlanListView.as_view(), name='plans'),
    path('current/', views.CurrentSubscriptionView.as_view(), name='current'),
    path('upgrade/', views.UpgradeSubscriptionView.as_view(), name='upgrade'),
    path('cancel/', views.CancelSubscriptionView.as_view(), name='cancel'),
    path('usage/', views.UsageView.as_view(), name='usage'),
]

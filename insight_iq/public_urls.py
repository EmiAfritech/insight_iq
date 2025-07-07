"""
Public URLs for shared/landing pages
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.public_urls')),
    path('dashboard/', include('core.urls')),  # Add dashboard routing
    path('subscriptions/', include('subscriptions.urls')),
    path('payments/', include('payments.urls')),
    path('accounts/', include('allauth.urls')),
    path('tenants/', include('tenants.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

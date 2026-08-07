from django.contrib import admin
from django.urls import path, include
from core.views import PublicSiteSettingsView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/modules/', include('modules.urls')),
    path('api/v1/admin/', include('core.urls')),
    path('api/v1/upload/', include('core.upload_urls')),
    path('api/v1/public-site-settings/', PublicSiteSettingsView.as_view(), name='public_site_settings'),
]

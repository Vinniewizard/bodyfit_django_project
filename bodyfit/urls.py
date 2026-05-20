
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import Http404
from core.admin import bodyfit_admin

# Only allow staff/superusers to access admin
def staff_admin_view(request, *args, **kwargs):
    if not request.user.is_authenticated or not request.user.is_staff:
        raise Http404()
    return bodyfit_admin.urls


urlpatterns = [
    path('admin/', bodyfit_admin.urls), # Using the custom admin site directly
    path('', include('core.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

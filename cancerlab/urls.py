# cancerlab/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",         include("apps.public.urls")),
    path("",         include("apps.accounts.urls")),
    path("equipamentos/", include("apps.bookings.urls")),
    path("interno/",      include("apps.internal.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import include, path

from apps.core.views import healthcheck


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
    path("", include("apps.catalog.urls")),
    path("", include("apps.payments.urls")),
]

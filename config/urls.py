from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.common.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.products.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),

    # Schema & docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Health
    path("api/health/", health_check, name="health-check"),
]

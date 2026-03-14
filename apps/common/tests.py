import pytest
from unittest.mock import MagicMock
from django.test import RequestFactory
from django.urls import reverse

from apps.common.permissions import IsOwnerOrAdmin, IsAdminOrReadOnly
from apps.common.throttles import BurstRateThrottle, SustainedRateThrottle, OrderCreateThrottle
from apps.common.pagination import StandardPagination

HEALTH_URL = reverse("health-check")


# ── Permissions ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestIsOwnerOrAdmin:
    def setup_method(self):
        self.permission = IsOwnerOrAdmin()

    def test_owner_allowed(self, user):
        obj = MagicMock()
        obj.user = user
        request = MagicMock()
        request.user = user
        assert self.permission.has_object_permission(request, None, obj) is True

    def test_admin_allowed(self, admin_user, user):
        obj = MagicMock()
        obj.user = user
        request = MagicMock()
        request.user = admin_user
        assert self.permission.has_object_permission(request, None, obj) is True

    def test_other_user_denied(self, user, db):
        from django.contrib.auth import get_user_model
        other = get_user_model().objects.create_user(
            email="other@example.com", username="other", password="pass12345"
        )
        obj = MagicMock()
        obj.user = user
        request = MagicMock()
        request.user = other
        assert self.permission.has_object_permission(request, None, obj) is False


@pytest.mark.django_db
class TestIsAdminOrReadOnly:
    def setup_method(self):
        self.permission = IsAdminOrReadOnly()

    def test_safe_methods_allowed(self, user):
        for method in ("GET", "HEAD", "OPTIONS"):
            request = MagicMock()
            request.method = method
            request.user = user
            assert self.permission.has_permission(request, None) is True

    def test_write_allowed_for_admin(self, admin_user):
        request = MagicMock()
        request.method = "POST"
        request.user = admin_user
        assert self.permission.has_permission(request, None) is True

    def test_write_denied_for_regular_user(self, user):
        request = MagicMock()
        request.method = "POST"
        request.user = user
        assert self.permission.has_permission(request, None) is False

    def test_write_denied_for_anonymous(self):
        request = MagicMock()
        request.method = "DELETE"
        request.user = None
        assert self.permission.has_permission(request, None) is False


# ── Throttles ─────────────────────────────────────────────────────────────────

class TestThrottleSetup:
    def test_burst_throttle_scope(self):
        assert BurstRateThrottle.scope == "burst"

    def test_sustained_throttle_scope(self):
        assert SustainedRateThrottle.scope == "sustained"

    def test_order_create_throttle_scope(self):
        assert OrderCreateThrottle.scope == "order_create"

    def test_throttle_cache_key_authenticated(self, user):
        throttle = BurstRateThrottle()
        request = MagicMock()
        request.user = user
        key = throttle.get_cache_key(request, None)
        assert str(user.pk) in key

    def test_throttle_cache_key_anonymous(self):
        throttle = BurstRateThrottle()
        request = MagicMock()
        request.user = MagicMock(is_authenticated=False)
        request.META = {"REMOTE_ADDR": "1.2.3.4"}
        # get_ident returns IP-based key
        throttle.get_ident = MagicMock(return_value="1.2.3.4")
        key = throttle.get_cache_key(request, None)
        assert "1.2.3.4" in key


# ── Pagination ────────────────────────────────────────────────────────────────

class TestStandardPagination:
    def test_defaults(self):
        p = StandardPagination()
        assert p.page_size == 20
        assert p.max_page_size == 100
        assert p.page_size_query_param == "page_size"


# ── Health Check ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestHealthCheck:
    def test_health_check_returns_ok(self, api_client):
        response = api_client.get(HEALTH_URL)
        assert response.status_code in (200, 503)
        assert "status" in response.data
        assert "components" in response.data
        assert "database" in response.data["components"]

    def test_health_check_db_component(self, api_client):
        response = api_client.get(HEALTH_URL)
        assert response.data["components"]["database"] == "ok"

    def test_health_check_no_auth_required(self, api_client):
        response = api_client.get(HEALTH_URL)
        assert response.status_code != 401


# ── Middleware ─────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRequestLoggingMiddleware:
    def test_middleware_logs_request(self, api_client):
        import logging
        logger = logging.getLogger("apps.common")
        records = []
        handler = logging.Handler()
        handler.emit = lambda record: records.append(record)
        logger.addHandler(handler)
        try:
            api_client.get(HEALTH_URL)
        finally:
            logger.removeHandler(handler)
        assert any("GET" in r.getMessage() and "health" in r.getMessage() for r in records)

    def test_middleware_includes_status_code(self, api_client):
        import logging
        logger = logging.getLogger("apps.common")
        records = []
        handler = logging.Handler()
        handler.emit = lambda record: records.append(record)
        logger.addHandler(handler)
        try:
            api_client.get(HEALTH_URL)
        finally:
            logger.removeHandler(handler)
        assert any("200" in r.getMessage() or "503" in r.getMessage() for r in records)

    def test_middleware_includes_duration(self, api_client):
        import logging
        logger = logging.getLogger("apps.common")
        records = []
        handler = logging.Handler()
        handler.emit = lambda record: records.append(record)
        logger.addHandler(handler)
        try:
            api_client.get(HEALTH_URL)
        finally:
            logger.removeHandler(handler)
        assert any("ms" in r.getMessage() for r in records)

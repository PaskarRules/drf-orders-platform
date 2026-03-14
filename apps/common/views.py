import logging

from django.db import connection
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger("apps.common")


@api_view(["GET"])
@permission_classes([AllowAny])
@throttle_classes([])
def health_check(request):
    health = {"status": "ok", "components": {}}

    # Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health["components"]["database"] = "ok"
    except Exception as e:
        health["status"] = "degraded"
        health["components"]["database"] = str(e)

    # Redis
    try:
        from django.core.cache import cache
        cache.set("health_check", "ok", 10)
        assert cache.get("health_check") == "ok"
        health["components"]["redis"] = "ok"
    except Exception as e:
        health["status"] = "degraded"
        health["components"]["redis"] = str(e)

    # Celery
    try:
        from config.celery import app as celery_app
        inspect = celery_app.control.inspect(timeout=2)
        if inspect.ping():
            health["components"]["celery"] = "ok"
        else:
            health["components"]["celery"] = "no workers"
            health["status"] = "degraded"
    except Exception as e:
        health["status"] = "degraded"
        health["components"]["celery"] = str(e)

    status_code = 200 if health["status"] == "ok" else 503
    return Response(health, status=status_code)

import logging
import time

logger = logging.getLogger("apps.common")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        try:
            response = self.get_response(request)
        except Exception:
            duration_ms = (time.monotonic() - start) * 1000
            logger.error(
                "%s %s 500 %.1fms",
                request.method,
                request.get_full_path(),
                duration_ms,
            )
            raise
        duration_ms = (time.monotonic() - start) * 1000

        logger.info(
            "%s %s %s %.1fms",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response

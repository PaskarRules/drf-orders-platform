from rest_framework.throttling import SimpleRateThrottle


class UserAwareRateThrottle(SimpleRateThrottle):
    """Base throttle that keys on user PK for authenticated users, IP otherwise."""

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class BurstRateThrottle(UserAwareRateThrottle):
    scope = "burst"


class SustainedRateThrottle(UserAwareRateThrottle):
    scope = "sustained"


class OrderCreateThrottle(UserAwareRateThrottle):
    scope = "order_create"

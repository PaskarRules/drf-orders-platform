import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Product

logger = logging.getLogger("apps.products")


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_product_cache(sender, instance, **kwargs):
    """Invalidate product caches by incrementing the version key.

    Old cache entries expire naturally via TTL, avoiding the need to
    call cache.clear() which would nuke unrelated cached data.
    """
    from .views import PRODUCT_CACHE_VERSION_KEY

    try:
        cache.incr(PRODUCT_CACHE_VERSION_KEY)
    except ValueError:
        cache.set(PRODUCT_CACHE_VERSION_KEY, 1)
    logger.debug("Product cache version incremented for %s", instance.slug)

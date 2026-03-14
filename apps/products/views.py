import logging

from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrReadOnly

from .filters import ProductFilter
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

logger = logging.getLogger("apps.products")

PRODUCT_CACHE_VERSION_KEY = "product_cache_version"


def _get_cache_version():
    """Return the current product cache version, initialising if needed."""
    version = cache.get(PRODUCT_CACHE_VERSION_KEY)
    if version is None:
        cache.set(PRODUCT_CACHE_VERSION_KEY, 1)
        return 1
    return version


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related("category").filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = ProductFilter
    search_fields = ("name", "sku", "description")
    ordering_fields = ("name", "price", "created_at")
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        version = _get_cache_version()
        cache_key = f"products:v{version}:list:{request.get_full_path()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 300)
        return response

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get("slug", "")
        version = _get_cache_version()
        cache_key = f"products:v{version}:detail:{slug}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 300)
        return response


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = "slug"

from django_filters import rest_framework as filters

from .models import Product


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = filters.CharFilter(field_name="category__slug")
    in_stock = filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model = Product
        fields = ["category", "is_active"]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity__lte=0)

from rest_framework import serializers

from apps.products.serializers import ProductSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "unit_price", "line_total")
        read_only_fields = ("id", "unit_price", "line_total")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "user_email", "status",
            "total_amount", "notes", "items", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "order_number", "status", "total_amount",
            "created_at", "updated_at",
        )


class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=10_000)


class CreateOrderSerializer(serializers.Serializer):
    items = CreateOrderItemSerializer(many=True)
    notes = serializers.CharField(required=False, default="")

from django.db import models, transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsOwnerOrAdmin
from apps.common.throttles import OrderCreateThrottle
from apps.notifications.tasks import send_order_notification

from .models import Order
from .serializers import OrderSerializer, CreateOrderSerializer
from .services import create_order, cancel_order


class OrderListCreateView(generics.ListCreateAPIView):
    """List orders for the current user, or create a new order."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_throttles(self):
        if self.request.method == "POST":
            return [OrderCreateThrottle()]
        return super().get_throttles()

    def get_queryset(self) -> models.QuerySet:
        user = self.request.user
        qs = Order.objects.select_related("user").prefetch_related("items__product")
        if not user.is_staff:
            qs = qs.filter(user=user)
        return qs

    def create(self, request, *args, **kwargs) -> Response:
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(
            user=request.user,
            items_data=serializer.validated_data["items"],
            notes=serializer.validated_data.get("notes", ""),
        )
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a single order by its order number."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)
    lookup_field = "order_number"

    def get_queryset(self) -> models.QuerySet:
        return Order.objects.prefetch_related("items__product")


class OrderCancelView(generics.GenericAPIView):
    """Cancel a pending order."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrAdmin)
    lookup_field = "order_number"

    def get_queryset(self) -> models.QuerySet:
        return Order.objects.prefetch_related("items__product")

    def post(self, request, *args, **kwargs) -> Response:
        order = self.get_object()
        order = cancel_order(order)
        transaction.on_commit(
            lambda: send_order_notification.delay(order.id, "order_cancelled")
        )
        return Response(OrderSerializer(order).data)

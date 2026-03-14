from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils.crypto import get_random_string
from django.utils import timezone

from apps.products.models import Product

from .exceptions import EmptyOrderError, InsufficientStockError, InvalidOrderStateError, ProductNotFoundError
from .models import Order, OrderItem

if TYPE_CHECKING:
    from apps.accounts.models import User

logger = logging.getLogger("apps.orders")


def generate_order_number() -> str:
    """Generate a unique order number in ORD-YYYYMMDD-XXXXX format."""
    date_part = timezone.now().strftime("%Y%m%d")
    random_part = get_random_string(8, "0123456789")
    return f"ORD-{date_part}-{random_part}"


@transaction.atomic
def create_order(
    user: User,
    items_data: list[dict],
    notes: str = "",
) -> Order:
    """Create an order with transactional stock validation.

    Acquires row-level locks via select_for_update to prevent
    overselling under concurrent requests.

    Raises:
        ProductNotFoundError: if a product ID doesn't exist or is inactive.
        InsufficientStockError: if requested quantity exceeds available stock.
    """
    if not items_data:
        raise EmptyOrderError()

    order = Order.objects.create(
        user=user,
        order_number=generate_order_number(),
        notes=notes,
    )

    total = Decimal("0.00")

    # Lock products for stock update
    product_ids = [item["product_id"] for item in items_data]
    products = {
        p.id: p
        for p in Product.objects.select_for_update().filter(id__in=product_ids, is_active=True)
    }

    for item_data in items_data:
        product_id = item_data["product_id"]
        quantity = item_data["quantity"]

        product = products.get(product_id)
        if not product:
            raise ProductNotFoundError()

        if product.stock_quantity < quantity:
            raise InsufficientStockError(
                product_name=product.name,
                available=product.stock_quantity,
            )

        product.stock_quantity -= quantity
        product.save(update_fields=["stock_quantity"])

        line_total = product.price * quantity
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
            line_total=line_total,
        )
        total += line_total

    order.total_amount = total
    order.save(update_fields=["total_amount"])

    logger.info("Order %s created for user %s, total: %s", order.order_number, user.email, total)
    return order


@transaction.atomic
def cancel_order(order: Order) -> Order:
    """Cancel an order and restore reserved stock.

    Raises:
        InvalidOrderStateError: if order is already completed, failed, or cancelled.
    """
    # Re-fetch with row lock to prevent race conditions where a concurrent
    # task (e.g. process_order) changes status between check and update.
    order = Order.objects.select_for_update().get(id=order.id)

    if not order.is_cancellable:
        raise InvalidOrderStateError(
            order_number=order.order_number,
            current_status=order.status,
        )

    items = list(order.items.all())
    product_ids = [item.product_id for item in items]
    products = {
        p.id: p
        for p in Product.objects.select_for_update().filter(id__in=product_ids)
    }

    for item in items:
        product = products[item.product_id]
        product.stock_quantity += item.quantity
        product.save(update_fields=["stock_quantity"])

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])

    logger.info("Order %s cancelled", order.order_number)
    return order

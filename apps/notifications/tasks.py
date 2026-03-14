import logging
import random

from celery import shared_task

logger = logging.getLogger("apps.notifications")

NOTIFICATION_TEMPLATES = {
    "order_created": {
        "title": "Order Created",
        "message": "Your order {order_number} has been placed successfully.",
    },
    "order_completed": {
        "title": "Order Completed",
        "message": "Your order {order_number} has been completed.",
    },
    "order_failed": {
        "title": "Order Failed",
        "message": "Your order {order_number} could not be processed. Please try again.",
    },
    "order_cancelled": {
        "title": "Order Cancelled",
        "message": "Your order {order_number} has been cancelled.",
    },
}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def send_order_notification(self, order_id, notification_type):
    """Create a notification record for an order status change."""
    from apps.orders.models import Order
    from apps.notifications.models import Notification

    try:
        order = Order.objects.select_related("user").get(id=order_id)
    except Order.DoesNotExist:
        logger.error("Order %s not found for notification", order_id)
        return

    template = NOTIFICATION_TEMPLATES.get(notification_type)
    if not template:
        logger.error("Unknown notification type: %s", notification_type)
        return

    try:
        _, created = Notification.objects.get_or_create(
            order=order,
            notification_type=notification_type,
            defaults={
                "user": order.user,
                "title": template["title"],
                "message": template["message"].format(order_number=order.order_number),
            },
        )
        if created:
            logger.info(
                "Notification '%s' sent for order %s", notification_type, order.order_number
            )
        else:
            logger.info(
                "Notification '%s' already exists for order %s", notification_type, order.order_number
            )
    except Exception as exc:
        backoff = (2 ** self.request.retries) * 5 + random.uniform(0, 3)
        try:
            self.retry(exc=exc, countdown=backoff)
        except self.MaxRetriesExceededError:
            logger.error(
                "Notification '%s' for order %s failed after max retries",
                notification_type,
                order.order_number,
            )

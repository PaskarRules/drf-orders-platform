import logging
import random

from celery import shared_task

from .models import Order

logger = logging.getLogger("apps.orders")


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def process_order(self, order_id):
    """Process an order asynchronously with retry + exponential backoff."""
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error("Order %s not found", order_id)
        return

    if order.status != Order.Status.PENDING:
        logger.info("Order %s already in status %s, skipping", order.order_number, order.status)
        return

    order.status = Order.Status.PROCESSING
    order.save(update_fields=["status"])
    logger.info("Processing order %s", order.order_number)

    try:
        # Simulate processing (payment, fulfillment, etc.)
        order.status = Order.Status.COMPLETED
        order.save(update_fields=["status"])
        logger.info("Order %s completed", order.order_number)

        # Trigger notification
        from apps.notifications.tasks import send_order_notification
        send_order_notification.delay(order.id, "order_completed")

    except Exception as exc:
        logger.error("Order %s processing failed: %s", order.order_number, exc)
        # Exponential backoff with jitter
        backoff = (2 ** self.request.retries) * 10 + random.uniform(0, 5)
        try:
            self.retry(exc=exc, countdown=backoff)
        except self.MaxRetriesExceededError:
            order.status = Order.Status.FAILED
            order.save(update_fields=["status"])
            logger.error("Order %s failed after max retries", order.order_number)

            from apps.notifications.tasks import send_order_notification
            send_order_notification.delay(order.id, "order_failed")

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    if created:
        from apps.orders.tasks import process_order
        from apps.notifications.tasks import send_order_notification
        transaction.on_commit(lambda: (
            process_order.delay(instance.id),
            send_order_notification.delay(instance.id, "order_created"),
        ))

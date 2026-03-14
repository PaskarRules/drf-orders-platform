from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class Notification(TimeStampedModel):
    class NotificationType(models.TextChoices):
        ORDER_CREATED = "order_created", "Order Created"
        ORDER_COMPLETED = "order_completed", "Order Completed"
        ORDER_FAILED = "order_failed", "Order Failed"
        ORDER_CANCELLED = "order_cancelled", "Order Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "notification_type"],
                name="unique_order_notification",
            ),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.user.email}"

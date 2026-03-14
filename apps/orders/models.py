from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class OrderQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=Order.Status.PENDING)

    def completed(self):
        return self.filter(status=Order.Status.COMPLETED)

    def failed(self):
        return self.filter(status=Order.Status.FAILED)

    def cancelled(self):
        return self.filter(status=Order.Status.CANCELLED)

    def for_user(self, user):
        return self.filter(user=user)

    def with_items(self):
        return self.prefetch_related("items__product")

    def total_revenue(self):
        return self.completed().aggregate(
            revenue=models.Sum("total_amount"),
        )["revenue"] or Decimal("0.00")


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    order_number = models.CharField(max_length=30, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.order_number

    @property
    def is_cancellable(self) -> bool:
        return self.status in (self.Status.PENDING, self.Status.PROCESSING)

    @property
    def item_count(self) -> int:
        return self.items.count()


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)

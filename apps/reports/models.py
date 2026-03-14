from django.db import models

from apps.common.models import TimeStampedModel


class DailyOrderReport(TimeStampedModel):
    report_date = models.DateField(unique=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    completed_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    cancelled_count = models.PositiveIntegerField(default=0)
    avg_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    report_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-report_date"]

    def __str__(self):
        return f"Report {self.report_date}"

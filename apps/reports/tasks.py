import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone

logger = logging.getLogger("apps.reports")


@shared_task
def generate_daily_order_report():
    """Generate a daily summary report for the previous day's orders."""
    from apps.orders.models import Order
    from apps.reports.models import DailyOrderReport

    yesterday = (timezone.now() - timedelta(days=1)).date()

    orders = Order.objects.filter(created_at__date=yesterday)
    stats = orders.aggregate(
        total_orders=Count("id"),
        total_revenue=Sum("total_amount"),
        avg_order_value=Avg("total_amount"),
        completed_count=Count("id", filter=Q(status=Order.Status.COMPLETED)),
        failed_count=Count("id", filter=Q(status=Order.Status.FAILED)),
        cancelled_count=Count("id", filter=Q(status=Order.Status.CANCELLED)),
        pending_count=Count("id", filter=Q(status=Order.Status.PENDING)),
        processing_count=Count("id", filter=Q(status=Order.Status.PROCESSING)),
    )

    _, created = DailyOrderReport.objects.get_or_create(
        report_date=yesterday,
        defaults={
            "total_orders": stats["total_orders"] or 0,
            "total_revenue": stats["total_revenue"] or Decimal("0.00"),
            "avg_order_value": stats["avg_order_value"] or Decimal("0.00"),
            "completed_count": stats["completed_count"] or 0,
            "failed_count": stats["failed_count"] or 0,
            "cancelled_count": stats["cancelled_count"] or 0,
            "report_data": {
                "pending_count": stats["pending_count"] or 0,
                "processing_count": stats["processing_count"] or 0,
            },
        },
    )

    if created:
        logger.info("Daily report generated for %s: %d orders", yesterday, stats["total_orders"] or 0)
    else:
        logger.info("Report for %s already exists, skipping", yesterday)

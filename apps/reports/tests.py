import pytest
from datetime import timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone

from apps.orders.models import Order
from apps.orders.services import create_order
from apps.reports.models import DailyOrderReport
from apps.reports.tasks import generate_daily_order_report

REPORT_URL = reverse("reports:daily-report")


@pytest.mark.django_db
class TestDailyReport:
    def test_generate_report(self, user, product):
        order = create_order(user, [{"product_id": product.id, "quantity": 2}])
        order.status = Order.Status.COMPLETED
        order.save()
        # Backdate to yesterday
        yesterday = timezone.now() - timedelta(days=1)
        Order.objects.filter(id=order.id).update(created_at=yesterday)

        generate_daily_order_report()

        report = DailyOrderReport.objects.get(report_date=yesterday.date())
        assert report.total_orders == 1
        assert report.total_revenue == Decimal("59.98")
        assert report.completed_count == 1

    def test_report_idempotent(self, user, product):
        yesterday = (timezone.now() - timedelta(days=1)).date()
        DailyOrderReport.objects.create(report_date=yesterday)
        generate_daily_order_report()
        assert DailyOrderReport.objects.filter(report_date=yesterday).count() == 1

    def test_report_endpoint_admin_only(self, auth_client):
        response = auth_client.get(REPORT_URL)
        assert response.status_code == 403

    def test_report_endpoint_admin(self, admin_client):
        response = admin_client.get(REPORT_URL)
        assert response.status_code == 200

from rest_framework import serializers

from .models import DailyOrderReport


class DailyOrderReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyOrderReport
        fields = (
            "id",
            "report_date",
            "total_orders",
            "total_revenue",
            "completed_count",
            "failed_count",
            "cancelled_count",
            "avg_order_value",
            "report_data",
            "created_at",
            "updated_at",
        )

from django.contrib import admin

from .models import DailyOrderReport


@admin.register(DailyOrderReport)
class DailyOrderReportAdmin(admin.ModelAdmin):
    list_display = ("report_date", "total_orders", "total_revenue", "completed_count", "failed_count")
    ordering = ("-report_date",)

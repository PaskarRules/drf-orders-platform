from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("daily/", views.DailyOrderReportListView.as_view(), name="daily-report"),
]

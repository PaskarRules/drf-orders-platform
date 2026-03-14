import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Fix the beat schedule crontab (can't serialize crontab in settings dict)
app.conf.beat_schedule = {
    "generate-daily-order-report": {
        "task": "apps.reports.tasks.generate_daily_order_report",
        "schedule": crontab(minute=0, hour=2),
    },
}

app.autodiscover_tasks()

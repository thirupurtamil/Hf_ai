# ts/ts/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ts.settings")

app = Celery("ts")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Beat schedule: fetch every 5 seconds
app.conf.beat_schedule = {
    "fetch-nse-every-5-sec": {
        "task": "home.tasks.fetch_nse_data",
        "schedule": 5.0,   # seconds
    },
}
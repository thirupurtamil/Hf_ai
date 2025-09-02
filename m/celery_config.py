"""
Celery configuration for mobile_ai_django project
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobile_ai_django.settings')

app = Celery('mobile_ai_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Celery Beat configuration for periodic tasks
app.conf.beat_schedule = {
    'update-daily-metrics': {
        'task': 'ai_chatbot.tasks.update_daily_metrics',
        'schedule': 300.0,  # Every 5 minutes for testing, change to daily in production
    },
    'daily-web-search-and-rating': {
        'task': 'ai_chatbot.tasks.daily_web_search_and_rating',
        'schedule': 86400.0,  # Daily
    },
    'weekly-auto-fine-tune': {
        'task': 'ai_chatbot.tasks.weekly_auto_fine_tune',
        'schedule': 604800.0,  # Weekly
    },
    'cleanup-old-data': {
        'task': 'ai_chatbot.tasks.cleanup_old_data',
        'schedule': 2592000.0,  # Monthly
    },
    'generate-weekly-report': {
        'task': 'ai_chatbot.tasks.generate_weekly_report',
        'schedule': 604800.0,  # Weekly
    },
    'sync-web-search-data': {
        'task': 'ai_chatbot.tasks.sync_web_search_data',
        'schedule': 43200.0,  # Twice daily
    },
}

app.conf.timezone = 'Asia/Kolkata'

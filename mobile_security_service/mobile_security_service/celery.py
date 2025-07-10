from django.conf import settings
import os
from celery import Celery
from celery import shared_task
import redis


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobile_security_service.settings')
app = Celery('mobile_security_service',)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.worker_pool = 'solo'
app.autodiscover_tasks()

@shared_task
def debug_task():
    print(f'Request: Holy shit')

from celery import shared_task
import celery.worker
from .analysis import analyze_app
from .models import UploadFile
from celery import Celery
from django.apps import apps
from django.core.files.storage import default_storage
import celery
from celery.utils.log import get_task_logger

@shared_task()
def process_file_async(analysisFilePath):
    file = default_storage.open(analysisFilePath, "rb")
    result = analyze_app(file)
    return result
        
    
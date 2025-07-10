from celery import shared_task
import celery.worker
from .analysis import analyze_app
from .models import UploadFile
from celery import Celery
from django.apps import apps
from django.core.files.storage import default_storage
import celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task()
def process_file_async(analysisFilePath, respond):
    pass
    # print(analysisFilePath)
    # with(default_storage.open(analysisFilePath)) as file:
    #     uploaded = UploadFile.objects.create(file=file, status='processing')
    #     analyze_app(uploaded, respond)
        
    
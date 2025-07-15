from celery import shared_task
import celery.worker
from .analysis import upload_app, static_analysis, get_results_report
from .models import UploadFile
from celery import Celery
from django.apps import apps
from django.core.files.storage import default_storage
import celery
from celery.utils.log import get_task_logger

@shared_task()
def process_file_async(analysisFilePath):
    result = ''
    file = default_storage.open(analysisFilePath, "rb")
    file_hash = upload_app(file, analysisFilePath)
    analysis_status = static_analysis(file_hash)
    report = get_results_report(analysis_status, file_hash)
    # scan_results=get_scan_results(analysis_status, file_hash)

    result+=report
    return result

        
    
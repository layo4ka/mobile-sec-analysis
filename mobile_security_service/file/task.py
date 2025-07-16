from celery import shared_task
import celery.worker
from .analysis import upload_app, static_analysis, get_results_report
from .models import UploadFile
from celery import Celery
from django.apps import apps
from django.core.files.storage import default_storage
import celery
from celery.utils.log import get_task_logger
from androguard.core.analysis.analysis import Analysis
from django.core.exceptions import ValidationError

# def check_apk():
#     # Ставим сюда, чтобы проверить файл ДО загрузки
#     file.seek(0)  # на всякий случай вернём курсор в начало
#     try:
#         apk = APK(file.read())
#         # тут можно добавить дополнительные проверки, например:
#         # if not apk.is_valid_APK(): raise ValidationError("Не APK")
#     except Exception:
#         raise ValidationError("Файл не похож на APK")
#     file.seek(0)  # снова вернём курсор в начало, чтобы upload_file() его прочитал правильно



@shared_task()
def process_file_async(analysisFilePath):
    result = ''
    file = default_storage.open(analysisFilePath, "rb")

    file_hash = upload_app(file, analysisFilePath)
    analysis_status = static_analysis(file_hash)
    report = get_results_report(analysis_status, file_hash)
    return report

        
    
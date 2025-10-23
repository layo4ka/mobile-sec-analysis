from celery import shared_task
import os
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# Попробуйте импортировать ваши функции анализа; если их нет — нужно будет адаптировать
try:
    from .analysis import upload_app, static_analysis, get_results_report
except Exception:
    upload_app = None
    static_analysis = None
    get_results_report = None
    logger.warning("Module file.analysis not found or missing functions. Task will try a minimal flow.")

@shared_task()
def process_file_async(analysisFilePath):
    """
    Принимает путь внутри storage (название файла), пытается:
    - загрузить файл в MobSF (через upload_app)
    - вызвать static_analysis и получить hash/идентификатор
    - запросить PDF (/api/v1/download_pdf) и записать в media/reports/
    - сформировать итоговый dict и вернуть
    """
    result = {
        "status": "error",
        "message": "Неизвестная ошибка",
        "analysis": None,
        "pdf_url": None
    }

    try:
        # Откроем файл из default_storage как бинарный поток
        f = default_storage.open(analysisFilePath, "rb")
    except Exception as e:
        result["message"] = f"Не удалось открыть файл: {e}"
        return result

    # 1) Загрузка в MobSF (если доступна функция upload_app)
    try:
        file_hash = None
        if upload_app:
            # upload_app должен принимать (file_object, filename) и возвращать hash/ид
            file_hash = upload_app(f, analysisFilePath)
        else:
            # Если upload_app нет — попробуем минимально: отправить POST на MOBSF напрямую
            mobsf_url = getattr(settings, "MOBSF_URL", None)
            mobsf_api_key = getattr(settings, "MOBSF_API_KEY", None)
            if mobsf_url:
                uploadURL = f"{mobsf_url}/api/v1/upload"
                headers = {}
                if mobsf_api_key:
                    headers["Authorization"] = mobsf_api_key
                f.seek(0)
                files = {'file': (os.path.basename(analysisFilePath), f, 'application/octet-stream')}
                resp = requests.post(uploadURL, files=files, headers=headers, timeout=60)
                try:
                    j = resp.json()
                    # MobSF отвечает {'hash': '<hash>'} или similar
                    if isinstance(j, dict):
                        file_hash = j.get('hash') or j.get('scan_hash') or j.get('scan') or None
                except Exception:
                    file_hash = None

        # 2) Статический анализ: вызвать static_analysis, получить структуру результатов
        analysis_status = None
        if static_analysis and file_hash:
            try:
                analysis_status = static_analysis(file_hash)
            except Exception as e:
                logger.warning("static_analysis failed: %s", e)
                analysis_status = None

        # 3) Попытка получить PDF от MobSF по hash
        pdf_saved = None
        try:
            mobsf_url = getattr(settings, "MOBSF_URL", None)
            mobsf_api_key = getattr(settings, "MOBSF_API_KEY", None)
            hash_for_pdf = None
            # попытки найти hash в разных местах
            if isinstance(analysis_status, dict):
                hash_for_pdf = analysis_status.get('hash') or analysis_status.get('scan_hash') or analysis_status.get('scan')
            if not hash_for_pdf:
                hash_for_pdf = file_hash

            if mobsf_url and hash_for_pdf:
                download_url = f"{mobsf_url}/api/v1/download_pdf"
                headers = {}
                if mobsf_api_key:
                    headers['Authorization'] = mobsf_api_key
                # MobSF API ожидает form-data с 'hash'
                resp = requests.post(download_url, data={'hash': hash_for_pdf}, headers=headers, stream=True, timeout=120)
                if resp.status_code == 200 and resp.headers.get('content-type','').lower().startswith('application/pdf'):
                    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
                    os.makedirs(reports_dir, exist_ok=True)
                    pdf_filename = f"{hash_for_pdf}.pdf"
                    pdf_path = os.path.join(reports_dir, pdf_filename)
                    with open(pdf_path, 'wb') as pf:
                        for chunk in resp.iter_content(1024):
                            if chunk:
                                pf.write(chunk)
                    pdf_saved = os.path.join(settings.MEDIA_URL.lstrip('/'), 'reports', pdf_filename)
                else:
                    logger.warning("MobSF PDF error: status %s, body: %s", resp.status_code, resp.text[:200] if resp.text else '')
        except Exception as e:
            logger.warning("Error while trying to fetch PDF from MobSF: %s", e)

        # 4) Собираем итоговый анализ — если есть get_results_report используем его
        analysis_result = None
        if get_results_report:
            try:
                # try to pass analysis_status/file_hash depending on signature
                analysis_result = get_results_report(analysis_status if analysis_status else file_hash, file_hash)
            except Exception as e:
                logger.warning("get_results_report failed: %s", e)
                analysis_result = analysis_status or file_hash
        else:
            analysis_result = analysis_status or file_hash

        # Формируем финальный результат
        result["status"] = "ok"
        result["message"] = "Анализ завершён"
        result["analysis"] = analysis_result
        result["pdf_url"] = pdf_saved  # это должен быть путь типа 'media/reports/<hash>.pdf' (без ведущего /) или None
        return result

    except Exception as e:
        logger.exception("process_file_async unexpected error")
        result["message"] = f"Ошибка анализа: {e}"
        return result
    finally:
        try:
            f.close()
        except Exception:
            pass

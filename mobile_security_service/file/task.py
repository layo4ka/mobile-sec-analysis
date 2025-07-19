from celery import shared_task
import os, time, requests
from django.core.files.storage import default_storage
from django.conf import settings
from .analysis import upload_app  # только upload_app

@shared_task
def process_file_async(file_path):
    # даём MobSF стартануть
    time.sleep(10)

    # 1) загружаем файл в MobSF, получаем scan_hash
    with default_storage.open(file_path, "rb") as f:
        scan_hash = upload_app(f, file_path)

    # 2) генерируем PDF-отчёт
    pdf_resp = requests.post(
        f"{settings.MOBSF_URL}/api/v1/download_pdf",
        data={"hash": scan_hash},
        headers={"Authorization": settings.MOBSF_API_KEY},
        stream=True
    )
    pdf_url = None
    if pdf_resp.status_code == 200:
        reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        pdf_path = os.path.join(reports_dir, f"{scan_hash}.pdf")
        with open(pdf_path, "wb") as out:
            for chunk in pdf_resp.iter_content(1024):
                out.write(chunk)
        pdf_url = f"/media/reports/{scan_hash}.pdf"
    else:
        print("MobSF PDF error:", pdf_resp.text)

    # 3) возвращаем только нужное
    return {
        "scan_hash": scan_hash,
        "pdf_url": pdf_url
    }

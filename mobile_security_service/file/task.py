from celery import shared_task
import os, time, requests
from django.core.files.storage import default_storage
from django.conf import settings
from .analysis import upload_app  # только upload_app

@shared_task
def process_file_async(file_path):
    import time, os, requests
    from django.core.files.storage import default_storage
    from django.conf import settings
    from .analysis import upload_app

    # 1) даём MobSF стартапнуться
    time.sleep(10)

    # 2) загружаем файл и получаем hash
    with default_storage.open(file_path, "rb") as f:
        scan_hash = upload_app(f, file_path)

    # 3) запускаем статический анализ: указываем тип скана
    scan_type = 'ios' if file_path.lower().endswith('.ipa') else 'apk'
    resp_scan = requests.post(
        f"{settings.MOBSF_URL}/api/v1/scan",
        data={'hash': scan_hash, 'scan_type': scan_type},
        headers={'Authorization': settings.MOBSF_API_KEY},
        timeout=60
    )
    resp_scan.raise_for_status()  # упадет, если плохо

    # 4) скачиваем PDF после анализа
    pdf_resp = requests.post(
        f"{settings.MOBSF_URL}/api/v1/download_pdf",
        data={"hash": scan_hash},
        headers={"Authorization": settings.MOBSF_API_KEY},
        stream=True
    )

    # 5) сохраняем PDF, если всё ок
    pdf_url = None
    if pdf_resp.status_code == 200:
        pdf_dir = os.path.join(settings.MEDIA_ROOT, "reports")
        os.makedirs(pdf_dir, exist_ok=True)
        out_path = os.path.join(pdf_dir, f"{scan_hash}.pdf")
        with open(out_path, "wb") as out:
            for chunk in pdf_resp.iter_content(1024):
                out.write(chunk)
        pdf_url = f"/media/reports/{scan_hash}.pdf"
    else:
        print("MobSF PDF error:", pdf_resp.text)

    # 6) возвращаем результат
    return {"scan_hash": scan_hash, "pdf_url": pdf_url}

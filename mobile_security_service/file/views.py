from django.shortcuts import render
from .forms import UploadFileForm
from .models import UploadFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .task import process_file_async
from django.views.decorators.cache import cache_control
import os
from django.conf import settings
from django.http import FileResponse, Http404


def index(request):
    form = UploadFileForm()
    return render(request, 'file/index.html', {'form':form})

@csrf_exempt
def upload_file(request):
    if request.method != 'POST' or 'file' not in request.FILES:
        return JsonResponse({"error": "Требуется POST с файлом"}, status=400)

    uploaded = request.FILES['file']
    # сохраняем в модель, чтобы у нас был запись (необязательно, но оставляем)
    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"error": form.errors}, status=400)

    analysis = form.save(commit=False)
    analysis.save()

    # вызываем таску и ждём результат: она создаст PDF в media/reports/<hash>.pdf
    result = process_file_async.delay(analysis.file.path).get(timeout=120)
    scan_hash = result.get("scan_hash")
    if not scan_hash:
        return JsonResponse({"error": "Не удалось получить hash"}, status=500)

    # путь до PDF
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'reports', f"{scan_hash}.pdf")
    if not os.path.exists(pdf_path):
        raise Http404("PDF отчёт не найден")

    # отдаем PDF как скачиваемый файл
    response = FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f"report_{scan_hash}.pdf")
    return response

        
# @cache_control(private=True)
# def download_pdf_scan_results(request):
#     pass

def some_page(request):
    return JsonResponse({"shit":"shitty"})
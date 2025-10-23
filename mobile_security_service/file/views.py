from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .task import process_file_async
import os

def index(request):
    return render(request, 'index.html')  # теперь Django его найдет

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_path = default_storage.save(uploaded_file.name, uploaded_file)

        # Запуск асинхронного анализа
        result = process_file_async.delay(file_path).get()

        pdf_path = os.path.join('media', 'reports', f"{os.path.basename(file_path)}.pdf")
        pdf_url = f"/{pdf_path}" if os.path.exists(pdf_path) else None

        return JsonResponse({
            "status": "ok",
            "message": "Файл успешно проанализирован",
            "pdf_url": pdf_url,
            "analysis": result
        })
    return JsonResponse({"error": "Требуется POST с файлом"}, status=400)

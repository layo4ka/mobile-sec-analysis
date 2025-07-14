from django.shortcuts import render
from .forms import UploadFileForm
from .models import UploadFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .task import process_file_async
from django.views.decorators.cache import cache_control

def index(request):
    form = UploadFileForm()
    return render(request, 'file/index.html', {'form':form})

def upload_file(request):
    if request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        #print(request.FILES)
        if(form.is_valid()):
            analysis = form.save(commit=False)
            analysis.save()
            respnd=process_file_async.delay(analysis.file.path).get()
            return JsonResponse({"result":respnd})
        else:
            return JsonResponse({"error":form.errors})
        
@cache_control(private=True)
def download_pdf_scan_results(request):
    pass

def some_page(request):
    return JsonResponse({"shit":"shitty"})
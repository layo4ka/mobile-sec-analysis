from django.shortcuts import render
from .forms import UploadFileForm
from .models import UploadFile
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from django.http import JsonResponse


def index(request):
    form = UploadFileForm()
    return render(request, 'file/index.html', {'form':form})

def upload_file(request):
    if request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    
    return JsonResponse({"success":True})

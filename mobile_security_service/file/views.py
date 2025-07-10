from django.shortcuts import render
from .forms import UploadFileForm
from .models import UploadFile
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .task import process_file_async

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
            toRespond = {'status':'pending', 'results':''}
            print(analysis.file.path)
            process_file_async.delay('uploads/test.apk', toRespond)
            return JsonResponse({"status":toRespond['status'], "results":toRespond['results']})
        else:
            return JsonResponse({"error":form.errors})

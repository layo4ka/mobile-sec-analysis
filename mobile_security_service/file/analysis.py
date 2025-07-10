from .models import UploadFile

def analyze_app(file_instance, respond):
    try:
        file_instance.status = 'processsing'
        with(open(file_instance.file.path, 'rb')) as app:
            res = len(app.read())
        file_instance.results = res
        file_instance.status = 'completed'
        file_instance.save()
    except:
        file_instance.status = 'error'
        file_instance.save()
    print(file_instance.status, file_instance.results)
    respond['status'] = file_instance.status
    respond['results'] = file_instance.results
from django.db import models
from django.contrib.auth.models import User

class UploadFile(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    results = models.TextField(max_length=90,blank=True, null=True) #models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending', blank=True, null=True, choices=[
        ('pending', 'Ожидает анализа'),
        ('processing', 'Анализируется'),
        ('completed', 'Завершено'),
        ('error', 'Ошибка')
    ])
    


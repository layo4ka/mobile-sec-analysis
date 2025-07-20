import os
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from file import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload'),
    path('shitty/', views.some_page, name='shitty'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.authtoken'))
]

urlpatterns += static(
    settings.MEDIA_URL + "reports/",
    document_root=os.path.join(settings.MEDIA_ROOT, "reports")
)

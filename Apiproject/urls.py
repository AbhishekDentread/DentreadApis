
from django.contrib import admin
from django.urls import path
from api.views import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('authenticate/',  AuthenticateView.as_view()),
    path('uploadfile/', OrthancUploadfile.as_view(), name='upload'),
    path('azure/', FileUploadView.as_view(), name='upload'),
    path('fileup/', FileUploader.as_view(), name='upload'),
]

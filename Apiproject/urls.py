
from django.contrib import admin
from django.urls import path
from api.views import *
from api.tests import *

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('authenticate/',  AuthenticateView.as_view()),
    path('uploadfile/', OrthancUploadfile.as_view(), name='upload'),
    path('DownloanFile/', DownloanFile.as_view(), name='upload'),
]

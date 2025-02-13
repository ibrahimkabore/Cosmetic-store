from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from e_commerce.views import *

urlpatterns = [
     
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 =  custom_page_not_found_view
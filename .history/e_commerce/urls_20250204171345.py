from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from e_commerce.views import *
from django.conf.urls import handler404

urlpatterns = [
     
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 =  views.custom_page_not_found_view
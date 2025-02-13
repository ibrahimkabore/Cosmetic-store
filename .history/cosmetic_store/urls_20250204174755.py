 

from django.contrib import admin
from django.urls import path,include
from django.conf.urls import handler404
from e_commerce import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(' ', include('e_commerce.urls')),
]
handler404 =  views.custom_page_not_found_view
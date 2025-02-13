from django.urls import path,include
from e_commerce import views
 from django.conf.urls import handler404



handler404 =  views.custom_page_not_found_view
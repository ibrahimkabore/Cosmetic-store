from django.urls import path,include
from e_commerce import views
from django.conf.urls import handler404
from django.conf import settings

urlpatterns = [
    path('page/lecture/', views.votre_vue, name='votre_vue'),
    
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = views.page_not_found_view


 
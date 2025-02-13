from django.urls import path


urlpatterns = [
     
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


 
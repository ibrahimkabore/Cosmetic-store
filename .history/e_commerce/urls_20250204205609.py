from django.urls import path,include
from e_commerce import views
from django.conf.urls import handler404
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    
    #########################################################page home ####################################
    
    
    path('', lambda request: redirect('/accueil/', permanent=True))
    path('accueil/',acceuil,name='acceuil'),

     
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = views.page_not_found_view


 
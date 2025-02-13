from django.urls import path,include
from e_commerce import views
 

urlpatterns = [
    path('page/lecture/', views.votre_vue, name='votre_vue'),
]

handler404 = views.page_not_found_view


 
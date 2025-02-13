from django.urls import path,include
from e_commerce import views
from django.conf.urls import handler500, handler404, handler403, handler400


urlpatterns = [
    path('page/lecture/', views.votre_vue, name='votre_vue'),
]




handler404 = views.page_not_found_view
handler500 = views.page_not_found_view
handler400 = views.page_not_found_view
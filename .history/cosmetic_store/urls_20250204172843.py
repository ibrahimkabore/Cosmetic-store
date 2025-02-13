from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls import handler404

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('e_commerce.urls')),


] 
handler404 = views.custom_page_not_found_view
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


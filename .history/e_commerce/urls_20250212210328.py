from django.urls import path,include
from e_commerce import views
from django.conf.urls import handler404
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from e_commerce.views import *
 
 

urlpatterns = [
    ########################################## page home ####################################
    path('', lambda request: redirect('/Home/', permanent=True)),
    path('Home/',Home,name='Home'),
    
    ######################################## page detail ####################################
    path('Detail/<uuid:pk>/',Detail,name='Detail'),
    path('Detail/produit/<uuid:pk>/',Detail_product,name='Detail_product'),
    
    ######################################### url  product  #################################
    path('products/', ProductListView.as_view() , name='product'),
    
    ###################################### url  favoris  ####################################
    path ('favoris/',favorite_list,name='favoris'),
    path('toggle-favorite/<uuid:product_id>/',toggle_favorite, name='toggle-favorite'),    
    ###################################### url  contact  ####################################
    path ('contact/',contact,name='contact'),
    
     ###################################### url  shopping cart  ####################################
    path ('shoppingcart/',shoppingcart,name='shoppingcart'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_view, name='cart'),
    path('cart/update/', update_cart_item, name='update_cart_item'),
    path('cart/clear/', clear_cart, name='clear_cart'),


    ######################################## view de connexion  #######################
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('two-factor-method/', two_factor_method, name='two_factor_method'),
    path('email-verification/', email_verification, name='email_verification'),
    path('google-auth-verification/', google_auth_verification, name='google_auth_verification'),
    path('deconnexion',deconnection,name='deconnexion'),
    path('verify/', verify, name='verify'),
    
    ####################### view de recuperation de compte #######################
    path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/rest/password_reset_done.html'), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/rest/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/rest/password_reset_complete.html'), name='password_reset_complete'),
        

    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = views.page_not_found_view


 
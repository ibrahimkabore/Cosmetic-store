# views.py
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from e_commerce.models import *
 

def Home(request):
    user_favorites = []
    # Récupération des produits comme avant
    star_products = Product.objects.filter(star_product='Yes')
    recommended_products = Product.objects.filter(recommended='Yes')
    bestseller_products = Product.objects.filter(bestseller='Yes')
    recent_products = Product.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )
    
    # Vérifier si l'utilisateur est authentifié
    if request.user.is_authenticated:
        try:
            # Récupérer les favoris de l'utilisateur
            user_favorites = list(Favorite.objects.filter(
                user=request.user
            ).values_list('product_id', flat=True))
            user_favorites = [str(id) for id in user_favorites]
        except Exception as e:
            print(f"Error fetching favorites: {e}")
            user_favorites = []
            
    context = {
        'star_products': star_products,
        'recommended_products': recommended_products,
        'bestseller_products': bestseller_products,
        'recent_products': recent_products,
        'user_favorites': user_favorites,
     }
    
    return render(request, 'home/home.html', context)
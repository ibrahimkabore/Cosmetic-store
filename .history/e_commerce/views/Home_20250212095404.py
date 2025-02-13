# views.py
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from e_commerce.models import *

# @login_required
# def toggle_favorite(request, product_id):
#     if request.method == 'POST':
#         try:
#             product = Product.objects.get(id=product_id)
#             favorite = Favorite.objects.filter(user=request.user, product=product)
            
#             if favorite.exists():
#                 # Si le produit est déjà en favoris, on le retire
#                 favorite.delete()
#                 is_favorite = False
#             else:
#                 # Sinon, on l'ajoute aux favoris
#                 Favorite.objects.create(user=request.user, product=product)
#                 is_favorite = True
                
#             return JsonResponse({
#                 'status': 'success',
#                 'is_favorite': is_favorite
#             })
#         except Product.DoesNotExist:
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'Produit non trouvé'
#             }, status=404)
#     return JsonResponse({'status': 'error'}, status=400)

def Home(request):
    # Récupération des produits comme avant
    star_products = Product.objects.filter(star_product='Yes')
    recommended_products = Product.objects.filter(recommended='Yes')
    bestseller_products = Product.objects.filter(bestseller='Yes')
    recent_products = Product.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )
    
    # Ajout des favoris de l'utilisateur connecté
    user_favorites = []
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
    
    context = {
        'star_products': star_products,
        'recommended_products': recommended_products,
        'bestseller_products': bestseller_products,
        'recent_products': recent_products,
        'user_favorites': user_favorites
    }
    
    return render(request, 'home/home.html', context)
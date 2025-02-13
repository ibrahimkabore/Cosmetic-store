from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product,Favorite
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

@login_required
def favorite(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'home/favoris.html', {
        'favorites': favorites
    })

@login_required
def toggle_favorite(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if not created:
            favorite.delete()
            is_favorite = False
        else:
            is_favorite = True
            
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Product not found'
        }, status=404)
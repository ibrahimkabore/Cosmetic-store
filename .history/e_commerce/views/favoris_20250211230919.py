from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product,Favorite
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'home/favoris.html', {
        'favorites': favorites
    })


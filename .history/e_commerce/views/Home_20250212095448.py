# views.py
from datetime import timedelta
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from e_commerce.models import *
 

def Home(request):
    # Récupération des produits comme avant
    star_products = Product.objects.filter(star_product='Yes')
    recommended_products = Product.objects.filter(recommended='Yes')
    bestseller_products = Product.objects.filter(bestseller='Yes')
    recent_products = Product.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )
    
    
    context = {
        'star_products': star_products,
        'recommended_products': recommended_products,
        'bestseller_products': bestseller_products,
        'recent_products': recent_products,
     }
    
    return render(request, 'home/home.html', context)
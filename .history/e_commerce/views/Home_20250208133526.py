from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product
from django.utils import timezone
from datetime import timedelta

def Home(request):
    # List of star products
    star_products = Product.objects.filter(star_product='Yes')
    
    # List of recommended products
    recommended_products = Product.objects.filter(recommended='Yes')
    
    # List of bestseller products
    bestseller_products = Product.objects.filter(bestseller='Yes')
    
    # List of recent products
    recent_products = Product.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    )
    
    context = {
        'star_products': star_products,
        'recommended_products': recommended_products,
        'bestseller_products': bestseller_products,
        'recent_products': recent_products
    }
    
    return render(request, 'home/home.html', context)

def Detail (request,pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'home/detail.html', {'product': product})
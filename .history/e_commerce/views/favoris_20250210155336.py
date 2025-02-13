from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product
def favoris (request ):
    favorite_products = Product.objects.filter(favorite='Yes')
    
    return render(request, 'home/favoris.html',context)
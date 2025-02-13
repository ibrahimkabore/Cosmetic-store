from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
def favoris (request):
    favorite_products = Product.objects.filter(favorite='Yes')
    
    context={
        'favorite_products': favorite_products,  # List of favorite products
    }
    
    return render(request, 'home/favoris.html',context)
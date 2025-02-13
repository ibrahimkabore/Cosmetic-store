from django.http import HttpResponse
from django.shortcuts import render
from e_commerce.models import Product

def Home(request):
    
    # list of products star
    star_products = Product.objects.filter(star_product='Yes')
    print(star_products)
    
    
    
    return render(request, 'home/home.html',{'star_products': star_products})


 
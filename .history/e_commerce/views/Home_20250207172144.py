from django.http import HttpResponse
from django.shortcuts import render
from e_commerce.models import Product

def Home(request):
    
    return render(request, 'home/home.html')



def home_view(request):
    star_products = Product.objects.filter(star_product='Yes')
    return render(request,'home/home.html', {'star_products': star_products})
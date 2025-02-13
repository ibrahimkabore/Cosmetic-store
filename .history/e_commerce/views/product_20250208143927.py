from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product

def product(request, pk):

    return render(request, 'home/product.html')
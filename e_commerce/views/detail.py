from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product
def Detail (request,pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'home/detail.html', {'product': product})

def Detail_product (request,pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'home/detail_product.html', {'product': product})


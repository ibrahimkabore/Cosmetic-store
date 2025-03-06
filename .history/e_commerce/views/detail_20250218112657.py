from django.shortcuts import get_object_or_404, render
from e_commerce.models import CartItem, Product
def Detail (request,pk):
    product = get_object_or_404(Product, pk=pk)
    number =CartItem.objects.count
    return render(request, 'home/detail.html', {'product': product,'number': number})

def Detail_product (request,pk):
    product = get_object_or_404(Product, pk=pk)
    number =CartItem.objects.count
    return render(request, 'home/detail_product.html', {'product': product,'number': number})


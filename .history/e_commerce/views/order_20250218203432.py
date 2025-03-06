from django.shortcuts import get_object_or_404, render
from e_commerce.models import CartItem, Product
def commande (request,pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0
    return render(request, 'home/commande.html', {'product': product,'number': number})

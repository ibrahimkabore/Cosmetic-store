
from django.shortcuts import render
from e_commerce.models import CartItem, Order


def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0
    context = {
        'orders': orders,
        'number': number,
        'orders': orders
    }
    
   
    return render(request, 'home/commande.html', context)

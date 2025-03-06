
from django.shortcuts import render

from e_commerce.models import CartItem


def contact (request):
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0

    
    return render(request,'home/contact.html',{'number':number})
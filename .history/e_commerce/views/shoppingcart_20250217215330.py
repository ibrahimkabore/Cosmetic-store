from django.shortcuts import get_object_or_404, render
from e_commerce.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView,UpdateView,DeleteView,DetailView

@login_required
def cart_view(request):
    """View to display cart contents and handle cart updates"""
    try:
        cart = ShoppingCart.objects.get(user=request.user, is_active=True)
        cart_items = cart.cart_items.select_related('product').all()
        
        # Calculer les totaux pour chaque article
        for item in cart_items:
            item.total = item.product.price * item.quantity
        
        # Calculer le sous-total
        subtotal = sum(item.total for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'shipping_cost': Decimal('0.00'),
            'total': subtotal  # Ajouter les frais d'expédition si nécessaire
        }
        
        return render(request, 'home/ShoppingCart.html', context)
        
    except ShoppingCart.DoesNotExist:
        # If no active cart exists, show empty cart
        context = {
            'cart_items': [],
            'subtotal': Decimal('0.00'),
            'shipping_cost': Decimal('0.00'),
            'total': Decimal('0.00')
        }
    return render(request, 'home/ShoppingCart.html', context)


from django.http import JsonResponse
 
def remove_item_from_cart(request, item_id):
    try:
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.delete()
        return JsonResponse({'status': 'success'})
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error'}, status=400)



 
def update_cart_item_quantity(request, item_id):
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity'))
        try:
            cart_item = CartItem.objects.get(id=item_id)
            if new_quantity > 0 and new_quantity <= cart_item.product.stock_quantity:
                cart_item.quantity = new_quantity
                cart_item.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid quantity'}, status=400)
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=400)
 

def clear_cart(request):
    if request.method == 'POST':
        try:
            cart = ShoppingCart.objects.get(user=request.user, is_active=True)
            cart.cart_items.all().delete()
            return JsonResponse({'status': 'success'})
        except ShoppingCart.DoesNotExist:
            return JsonResponse({'status': 'error'}, status=400)

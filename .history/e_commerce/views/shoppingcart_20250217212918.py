from django.shortcuts import get_object_or_404, render
from e_commerce.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
 
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


from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
 

@login_required
def add_to_cart(request, product_id):
    """
    Function to add a product to the user's shopping cart.
    If the product is already in the cart, it increases the quantity.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Get or create the active cart for this user
        cart, created = ShoppingCart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
        
        # Check if this product is already in the cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        # If the item already existed, increase the quantity
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f"{product.name} a été ajouté à votre panier",
            'cart_count': CartItem.objects.filter(cart=cart).count()
        })
    
    return JsonResponse({
        'success': False,
        'message': "Méthode non autorisée"
    }, status=405)
    
    

@login_required
def update_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)

@login_required
def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)

@login_required
def clear_cart(request):
    if request.method == 'POST':
        cart = ShoppingCart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            CartItem.objects.filter(cart=cart).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)

@login_required
def update_cart(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        items = data.get('items', [])
        cart = ShoppingCart.objects.filter(user=request.user, is_active=True).first()
        if cart:
            for item in items:
                cart_item = CartItem.objects.filter(id=item['id'], cart=cart).first()
                if cart_item and int(item['quantity']) > 0:
                    cart_item.quantity = int(item['quantity'])
                    cart_item.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=405)
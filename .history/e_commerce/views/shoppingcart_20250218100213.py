from django.shortcuts import get_object_or_404, redirect, render
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

@login_required
def add_to_cart(request, product_id):
    """View to add a product to the cart"""
    try:
        product = Product.objects.get(id=product_id)
        cart = ShoppingCart.objects.get(user=request.user, is_active=True)
        
        # Check if the product already exists in the cart
        existing_item = CartItem.objects.filter(product=product, ShoppingCart=cart).first()
        
        if existing_item:
            # If the product exists, increase the quantity
            existing_item.quantity += 1
            existing_item.save()
            
        else:
            # If the product doesn't exist, create a new CartItem
            CartItem.objects.create(
                product=product,
                shopping_cart=cart,
                quantity=1
            )
            
        return redirect('home')
        
    except Product.DoesNotExist:
        return redirect('home')
    
@login_required
def remove_from_cart(request, cart_item_id):
    """View to remove a product from the cart"""
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id, shopping_cart__user=request.user, shopping_cart__is_active=True)
        cart_item.delete()
        return redirect('cart_view')
        
    except CartItem.DoesNotExist:
        return redirect('home')
    
@login_required
def update_cart_item(request, cart_item_id):
    """View to update the quantity of a product in the cart"""
    try:
        cart_item = get_object_or_404(CartItem, id=cart_item_id, shopping_cart__user=request.user, shopping_cart__is_active=True)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            cart_item.delete()
            
        else:
            cart_item.quantity = quantity
            cart_item.save()
            
        return redirect('cart_view')
        
    except CartItem.DoesNotExist:
        return redirect('home')
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

from django.http import JsonResponse
from uuid import UUID

@login_required
def add_to_cart(request, product_id):
    """View to add a product to the cart"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
        
    try:
       # Convertir la chaîne UUID en objet UUID si nécessaire
        if isinstance(product_id, str):
            product_id = UUID(product_id)
            
        product = Product.objects.get(id=product_id)
        
        # Vérifier si l'utilisateur a un panier actif
        cart, created = ShoppingCart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
        
        # Vérifier si le produit existe déjà dans le panier
        cart_item, created = CartItem.objects.get_or_create(
            product=product,
            shopping_cart=cart,
            defaults={'quantity': 0}
        )
        
        # Incrémenter la quantité
        cart_item.quantity += 1
        cart_item.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Produit ajouté au panier'
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Produit non trouvé'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
    
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
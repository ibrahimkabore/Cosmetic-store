from django.shortcuts import get_object_or_404, render
from e_commerce.models import *
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required



from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal

class CartManager:
    def __init__(self, user):
        self.user = user
        self.cart = self._get_or_create_cart()
    
    def _get_or_create_cart(self):
        """Get the user's active cart or create a new one if none exists."""
        cart, created = ShoppingCart.objects.get_or_create(
            user=self.user,
            is_active=True
        )
        return cart
    
    @transaction.atomic
    def add_to_cart(self, product_id, quantity=1):
        """
        Add a product to the cart or update its quantity if it already exists.
        
        Args:
            product_id: ID of the product to add
            quantity: Quantity to add (default=1)
            
        Returns:
            dict: Status of the operation and relevant messages
        """
        try:
            # Validate inputs
            if quantity < 1:
                raise ValidationError("Quantity must be at least 1")
                
            # Get the product
            product = get_object_or_404(Product, id=product_id)
            
            # Check if product is available
            if product.status != 'available':
                raise ValidationError("Product is not available")
                
            # Check stock availability
            if product.stock_quantity < quantity:
                raise ValidationError(f"Only {product.stock_quantity} items available in stock")
            
            # Check if product already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=self.cart,
                product=product,
                defaults={'quantity': 0}
            )
            
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            
            # Verify total quantity doesn't exceed stock
            if new_quantity > product.stock_quantity:
                raise ValidationError(f"Cannot add {quantity} more items. Only {product.stock_quantity - cart_item.quantity} additional items available")
            
            cart_item.quantity = new_quantity
            cart_item.save()
            
            return {
                'status': 'success',
                'message': f"Added {quantity} x {product.name} to cart",
                'cart_item': cart_item
            }
            
        except ValidationError as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': "An unexpected error occurred"
            }
    
    def get_cart_total(self):
        """Calculate the total price of all items in the cart."""
        total = Decimal('0.0')
        for item in self.cart.cart_items.all():
            price = item.product.price
            if item.product.discount_percentage:
                discount = (item.product.discount_percentage / 100) * price
                price = price - discount
            total += price * item.quantity
        return total.quantize(Decimal('0.01'))
    
    def get_cart_items(self):
        """Get all items in the cart with their details."""
        return self.cart.cart_items.all().select_related('product')


# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
 
@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        # Vérifier si le produit existe
        product = Product.objects.get(id=product_id)
        
        # Vérifier le stock
        if product.stock_quantity < quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'Stock insuffisant. Seulement {product.stock_quantity} disponible(s)'
            })
            
        # Récupérer ou créer le panier
        cart, _ = ShoppingCart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
        
        # Ajouter ou mettre à jour l'article dans le panier
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0}
        )
        
        # Mettre à jour la quantité
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock_quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'La quantité totale dépasse le stock disponible'
            })
            
        cart_item.quantity = new_quantity
        cart_item.save()
        
        # Compter le nombre total d'articles dans le panier
        cart_count = sum(item.quantity for item in cart.cart_items.all())
        
        return JsonResponse({
            'status': 'success',
            'message': f'{product.name} a été ajouté au panier',
            'cart_count': cart_count
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Produit non trouvé'
        })
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': 'Quantité invalide'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'Une erreur est survenue'
        })
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
def update_cart_item(request):
    """AJAX view to update cart item quantity"""
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 0))
        
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user,
                cart__is_active=True
            )
            
            if quantity > 0:
                if quantity <= cart_item.product.stock_quantity:
                    cart_item.quantity = quantity
                    cart_item.save()
                    new_total = cart_item.quantity * cart_item.product.price
                    return JsonResponse({
                        'status': 'success',
                        'new_quantity': quantity,
                        'new_total': str(new_total)
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Only {cart_item.product.stock_quantity} items available'
                    })
            else:
                cart_item.delete()
                return JsonResponse({
                    'status': 'removed'
                })
                
        except CartItem.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Item not found'
            })
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def clear_cart(request):
    """View to clear all items from cart"""
    if request.method == 'POST':
        try:
            cart = ShoppingCart.objects.get(user=request.user, is_active=True)
            cart.cart_items.all().delete()
            return JsonResponse({'status': 'success'})
        except ShoppingCart.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
 
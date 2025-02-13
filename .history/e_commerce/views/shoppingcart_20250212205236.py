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


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_manager = CartManager(request.user)
        result = cart_manager.add_to_cart(product_id, quantity)
        
        if result['status'] == 'success':
            return JsonResponse({
                'status': 'success',
                'message': result['message'],
                'cart_total': str(cart_manager.get_cart_total())
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': result['message']
            }, status=400)
            
    except ValueError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid quantity provided'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)
@login_required
def shoppingcart (request):
   
    
    return render(request, 'home/ShoppingCart.html')
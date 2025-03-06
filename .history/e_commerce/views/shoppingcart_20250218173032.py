from django.shortcuts import get_object_or_404, redirect, render
from e_commerce.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages

@login_required
def cart_view(request):
    
    cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    cart_items = cart.cart_items.select_related('product').all()
    number =CartItem.objects.count
    # Calculer les totaux pour chaque article
    for item in cart_items:
        item.total = item.product.price * item.quantity
    
    # Calculer le sous-total
    subtotal = sum(item.total for item in cart_items)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': Decimal('0.00'),
        'total': subtotal  ,# Ajouter les frais d'expédition si nécessaire
        'number': number,
        
    }
    
    return render(request, 'home/ShoppingCart.html', context)
     
 
 
def add_to_cart(request, product_id, redirect_url):
    """Fonction générique pour ajouter un produit au panier"""
    # Récupération du produit ou 404 si non trouvé
    product = get_object_or_404(Product, id=product_id)

    # Récupération ou création du panier actif pour l'utilisateur
    cart = ShoppingCart.objects.get(user=request.user, is_active=True)

    # Vérifier si l'élément existe déjà dans le panier
    existing_item = CartItem.objects.filter(product=product, cart=cart).first()

    if existing_item:
        # Si l'élément existe, augmenter la quantité
        existing_item.quantity += 1
        existing_item.save()
    else:
        # Si l'élément n'existe pas, créer un nouvel élément dans le panier
        CartItem.objects.create(product=product, cart=cart, quantity=1)

    # Affichage d'un message de succès
    messages.success(request, f"{product} ajouté au panier")

    # Redirection vers la page spécifiée
    return redirect(redirect_url)


@login_required
def add_to_cart_favoris(request, product_id):
    return add_to_cart(request, product_id, 'favoris')


@login_required
def add_to_cart_home(request, product_id):
    return add_to_cart(request, product_id, 'Home')


@login_required
def add_to_cart_product(request, product_id):
    return add_to_cart(request, product_id, 'product')


from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages

def update_cart_item_quantity(request):
    """
    Update the quantity of a specific cart item via AJAX.
    Expects POST parameters: item_id and quantity
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        # Vérifier si la quantité demandée est disponible en stock
        if quantity > cart_item.product.stock_quantity:
            return JsonResponse({
                'status': 'error',
                'message': 'Quantité non disponible en stock'
            }, status=400)
        
        if quantity < 1:
            quantity = 1
        
        cart_item.quantity = quantity
        cart_item.calculate_total_price()  # Mettre à jour le prix total
        cart_item.save()
        
        # Calculer le nouveau sous-total du panier
        cart = cart_item.cart
        subtotal = sum(item.total_price for item in cart.cart_items.all())
        
        return JsonResponse({
            'status': 'success',
            'item_total': cart_item.total_price,
            'subtotal': subtotal
        })
    
    return JsonResponse({'status': 'error'}, status=400)

def remove_cart_item(request):
    """
    Supprimer un élément spécifique du panier via AJAX.
    Attend le paramètre POST: item_id
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        
        cart = cart_item.cart
        cart_item.delete()
        
        # Calculer le nouveau sous-total
        subtotal = sum(item.total_price for item in cart.cart_items.all())
        
        return JsonResponse({
            'status': 'success',
            'subtotal': subtotal
        })
    
    return JsonResponse({'status': 'error'}, status=400)

def clear_cart(request):
    """
    Vider complètement le panier via AJAX
    """
    if request.method == 'POST':
        cart = ShoppingCart.objects.get(user=request.user, is_active=True)
        cart.cart_items.all().delete()
        
        return JsonResponse({
            'status': 'success',
            'subtotal': 0
        })
    
    return JsonResponse({'status': 'error'}, status=400)
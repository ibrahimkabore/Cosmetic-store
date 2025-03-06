from django.shortcuts import get_object_or_404, redirect, render
from e_commerce.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages

@login_required
def cart_view(request):
    
    if request.user.is_authenticated:
        number = CartItem.objects.filter(  ).count()
    else:
        number = 0 
        
        
    try:
        cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    except ShoppingCart.DoesNotExist:
        cart = None

    cart_items = cart.cart_items.select_related('product').all() if cart else []

    # Calculer les totaux pour chaque article
    for item in cart_items:
        item.total = item.product.price * item.quantity

    # Calculer le sous-total
    subtotal = sum(item.total for item in cart_items)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': Decimal('0.00'),
        'total': subtotal,  # Ajouter les frais d'expédition si nécessaire
        'number': number,  # Correction ici
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
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import uuid

@require_http_methods(["GET"])
def update_cart_item_quantity(request, item_id, quantity):
    """
    Met à jour la quantité d'un article dans le panier via URL
    L'item_id est maintenant un UUID
    """
    try:
        cart_item = get_object_or_404(CartItem, 
                                     id=item_id, 
                                     cart__user=request.user)
        
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
            messages.warning(request, "La quantité minimum est 1")
            
        # Vérifier le stock disponible
        if quantity > cart_item.product.stock_quantity:
            messages.error(request, 
                         f"Désolé, seulement {cart_item.product.stock_quantity} articles disponibles")
            quantity = cart_item.product.stock_quantity
            
        cart_item.quantity = quantity
        cart_item.calculate_total_price()
        cart_item.save()
        
        messages.success(request, "Quantité mise à jour avec succès")
        
    except ValueError:
        messages.error(request, "Quantité invalide")
    except uuid.uuid4:
        messages.error(request, "Article non trouvé")
    
    return redirect('cart')

@require_http_methods(["GET"])
def remove_cart_item(request, item_id):
    """
    Supprime un article spécifique du panier
    L'item_id est maintenant un UUID
    """
    try:
        cart_item = get_object_or_404(CartItem, 
                                     id=item_id, 
                                     cart__user=request.user)
        
        product_name = cart_item.product.name
        cart_item.delete()
        
        messages.error(request, f"{product_name} a été retiré du panier")
    except uuid.uuid4:
        messages.error(request, "Article non trouvé")
    
    return redirect('cart')

@require_http_methods(["GET"])
def clear_cart(request):
    """
    Vide complètement le panier
    """
    cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    cart.cart_items.all().delete()
    
    messages.error(request, "Votre panier a été vidé")
    return redirect('cart')
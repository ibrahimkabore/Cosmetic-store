from django.shortcuts import get_object_or_404, redirect, render
from e_commerce.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages

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

 
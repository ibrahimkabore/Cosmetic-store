from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from e_commerce.models import *
from e_commerce.views import order
from django.contrib import messages


 
def creer_commande(user, payment_method):
    try:
        # Récupérer le panier actif de l'utilisateur
        panier = ShoppingCart.objects.get(user=user, is_active=True)
        
        # Récupérer tous les items du panier
        cart_items = CartItem.objects.filter(cart=panier)
        
        if cart_items.exists():
            # Calculer le total d'abord
            total = sum(item.total_price for item in cart_items)
            
            # Créer la commande
            commande = Order.objects.create(
                user=user,
                payment_method=payment_method,
                total=total
            )
            
            # Créer les lignes de commande pour chaque item
            for item in cart_items:
                OrderLine.objects.create(
                    order=commande,          # Référence à la commande
                    product=item.product,    # Produit de l'item
                    quantity=item.quantity,  # Quantité
                    unit_price=item.product.price,  # Prix unitaire
                    line_total=item.total_price     # Total de la ligne
                )
            
            # Supprimer tous les items du panier
            cart_items.delete()
            
            # Désactiver le panier
            panier.is_active = True
            panier.save()
            
            return commande
            
    except ShoppingCart.DoesNotExist:
        return None
    
    return None

@login_required
def passer_commande(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Check if the payment method is valid
        if payment_method in dict(Order.PaymentMethod.choices):
            # Special case: if payment method is 'CASH', create the order and redirect to order_list
            if payment_method == Order.PaymentMethod.CASH:
                commande = creer_commande(request.user, payment_method)
                if commande:
                    messages.success(request, "Votre commande a été créée avec succès!")
                    return redirect('order_list')  # Redirect to order list if paying by cash
                else:
                    messages.error(request, "Votre panier est vide")
            else:
                # Handle other payment methods (e.g., CREDIT_CARD, MOBILE_MONEY)
                commande = creer_commande(request.user, payment_method)
                if commande:
                    messages.success(request, "Votre commande a été créée avec succès!")
                    return redirect('confirmation_commande', commande_id=commande.id)
                else:
                    messages.error(request, "Votre panier est vide")
        else:
            messages.error(request, "Méthode de paiement invalide")
    
    return redirect('order_list')


def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0
        
    
    status_filter = request.GET.get('status_filter', None)
    if status_filter:
        orders_filter = Order.objects.filter(status=status_filter)
    else:
        orders_filter = Order.objects.all()
    context = {
        'orders': orders,
        'number': number,
        'orders_filter': orders_filter
    }
    
   
    return render(request, 'home/commande.html', context)



@login_required
def checkout_view(request):
    # Récupérer le panier actif
    cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculer les totaux
    subtotal = sum(item.total_price for item in cart_items)
    print(subtotal)
    total = subtotal  # Ajoutez les frais de livraison si nécessaire
    
    if request.user.is_authenticated:
        number = CartItem.objects.filter(cart__user=request.user, cart__is_active=True).count()
    else:
        number = 0
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'number': number
    }
    return render(request, 'home/valider_commande.html', context)
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from e_commerce.models import *
from e_commerce.views import order
from django.contrib import messages


def creer_commande(user):
    # Récupérer le panier actif de l'utilisateur
    panier = ShoppingCart.objects.get(user=user, is_active=True)  # Ajustez selon votre logique
    
    # Récupérer tous les items du panier
    cart_items = CartItem.objects.filter(cart=panier)
    
    if cart_items.exists():
        # Créer une nouvelle commande
        commande = order.objects.create(user=user)
        
        # Calculer le total
        total = sum(item.total_price for item in cart_items)
        commande.total = total
        commande.save()
        
        # Vous pouvez aussi créer une table de liaison si nécessaire
        # Pour garder l'historique des produits commandés
        
        # Optionnel: désactiver le panier actuel
        panier.is_active = False
        panier.save()
        
        return commande
    
    return None

@login_required
def passer_commande(request):
    if request.method == 'POST':
        methode_paiement = request.POST.get('methode_paiement')
        if methode_paiement in dict(order.MethodePaiement.choices):
            commande = creer_commande(request.user, methode_paiement)
            if commande:
                return redirect('confirmation_commande', commande_id=commande.id)
            else:
                messages.error(request, "Votre panier est vide")
        else:
            messages.error(request, "Méthode de paiement invalide")
    return redirect('order_list')

 
 

def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'home/commande.html', context)



@login_required
def checkout_view(request):
    # Récupérer le panier actif
    cart = ShoppingCart.objects.get(user=request.user, is_active=True)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculer les totaux
    subtotal = sum(item.total_price for item in cart_items)
    total = subtotal  # Ajoutez les frais de livraison si nécessaire
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
    }
    return render(request, 'home/.html', context)
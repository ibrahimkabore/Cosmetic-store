from django.shortcuts import render

from e_commerce.models import *
from e_commerce.views import order
 
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
        if methode_paiement in dict(Commande.MethodePaiement.choices):
            commande = creer_commande(request.user, methode_paiement)
            if commande:
                return redirect('confirmation_commande', commande_id=commande.id)
            else:
                messages.error(request, "Votre panier est vide")
        else:
            messages.error(request, "Méthode de paiement invalide")
    return redirect('panier')

def commande(request):
    
    # Récupération de l'historique des commandes
    
    
    return render(request, 'home/commande.html')
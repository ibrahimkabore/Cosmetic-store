from django.shortcuts import render

from e_commerce.models import *
from e_commerce.views import order
 

def creer_commande(user, methode_paiement):
    panier = ShoppingCart.objects.get(user=user, is_active=True)
    cart_items = CartItem.objects.filter(cart=panier)
    
    if cart_items.exists():
        commande = order.objects.create(
            user=user,
            methode_paiement=methode_paiement
        )
        
        for item in cart_items:
            LigneCommande.objects.create(
                commande=commande,
                product=item.product,
                quantity=item.quantity,
                price_unitaire=item.product.price,
                total_ligne=item.total_price
            )
        
        commande.total = sum(ligne.total_ligne for ligne in commande.lignes.all())
        commande.save()
        
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
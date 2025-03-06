from django.shortcuts import render


def creer_commande(user, methode_paiement):
    panier = ShoppingCart.objects.get(user=user, is_active=True)
    cart_items = CartItem.objects.filter(cart=panier)
    
    if cart_items.exists():
        commande = Commande.objects.create(
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

def commande(request):
    
    # Récupération de l'historique des commandes
    
    
    return render(request, 'home/commande.html')
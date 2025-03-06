
from django.shortcuts import render


def history(request):
    
    # Récupération de l'historique des commandes
    history = request.session.get('history', [])
    
    # Récupération des produits et des prix correspondants
    products = Product.objects.all()
    prices = {product.id: product.price for product in products}
    
    # Création du contexte
    context = {
        'history': history,
        'prices': prices
    }
    
    return render(request, 'home/history.html', context)
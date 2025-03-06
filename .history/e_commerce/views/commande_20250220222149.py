from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from e_commerce.models import *
from e_commerce.views import order
from django.contrib import messages
from django.templatetags.static import static

 
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def envoyer_notification_commande(request,commande):
    """
    Envoie un email de notification avec les détails de la commande
    """
    # Récupérer les lignes de commande
    order_lines = OrderLine.objects.filter(order=commande)
    
    logo_url = request.build_absolute_uri(static('img/logo/ghislaine.png'))
    
    # Préparer le contexte pour le template
    context = {
        'user': commande.user,
        'commande': commande,
        'order_lines': order_lines,
        'total': commande.total,
        'date': commande.created_at.strftime('%d/%m/%Y %H:%M'),
        'logo': logo_url
    }
    
    # Générer le contenu de l'email
    sujet = f'Confirmation de votre commande #{commande.id}'
    message_text = f"""
    Bonjour {commande.user.get_full_name()},
    
    Votre commande #{commande.id} a été créée avec succès.
    
    Détails de la commande:
    Date: {commande.created_at.strftime('%d/%m/%Y %H:%M')}
    Mode de paiement: {commande.get_payment_method_display()}
    
    Articles commandés:
    {chr(10).join([f"- {line.product.name} x{line.quantity} : {line.line_total}€" for line in order_lines])}
    
    Total: {commande.total}€
    
    Merci de votre confiance!
    """
    
    # Générer la version HTML
    html_message = render_to_string('home/confirmation_commande.html', context)
    
    # Envoyer l'email
    send_mail(
        subject=sujet,
        message=message_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[commande.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    return response

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
                    order=commande,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price,
                    line_total=item.total_price
                )
            
            # Envoyer l'email de notification
            envoyer_notification_commande(commande)
            
            # Supprimer tous les items du panier
            cart_items.delete()
            
            # Désactiver le panier
            panier.is_active = True  # Correction: False au lieu de True

            panier.save()
            
            return commande
            
    except ShoppingCart.DoesNotExist:
        return None
    
    return None

@login_required
def passer_commande(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method in dict(Order.PaymentMethod.choices):
            commande = creer_commande(request.user, payment_method)
            if commande:
                messages.success(request, "Votre commande a été créée avec succès!")
                if payment_method == Order.PaymentMethod.CASH:
                    return redirect('order_list')
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
    context = {
        'orders': orders,
        'number': number,
        'orders': orders
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
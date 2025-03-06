from django.shortcuts import get_object_or_404, render
from e_commerce.models import *
from django.contrib.auth.decorators import login_required
from decimal import Decimal
 
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


@method_decorator(login_required, name='dispatch')
class DossierDeleteView( DeleteView):
    model = Dossier
    template_name = "pages/Dossier/Dossier_confirm_delete.html"
    success_url = reverse_lazy('Dossier_list')
    form_invalid_message = _("Oups, quelque chose s'est mal passé lors de la suppression!")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _("Le Dossier a été supprimé avec succès!"))
        return super().delete(request, *args, **kwargs)

    def get_object(self, **kwargs):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Dossier, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['method'] = "delete"
        return context 
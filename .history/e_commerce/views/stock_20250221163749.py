from datetime import timezone
from django.shortcuts import redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.db.models import Sum, F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from e_commerce.forms import ProductForm
from e_commerce.models import CartItem, Category, ParentCategory, Product

class ProductsListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'stock/product_list.html'
    context_object_name = 'products'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['parent_categories'] = ParentCategory.objects.all()
        context['search_name'] = self.request.GET.get('search_name', '')
        context['category_id'] = self.request.GET.get('category', '')
        context['parent_category_id'] = self.request.GET.get('parent_category', '')
        for product in context['products']:
            cart_items_quantity = CartItem.objects.filter(
                product=product
            ).aggregate(
                total_quantity=Sum('quantity')
            )['total_quantity'] or 0
            
            product.available_quantity = product.stock_quantity - cart_items_quantity
            
            product.out=product.stock_quantity-product.available_quantity
            
            
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'stock/product_form.html'
    success_url = reverse_lazy('product-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'stock/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'stock/product_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Calculate items in carts
        cart_items_quantity = CartItem.objects.filter(
            product=product
        ).aggregate(
            total_quantity=Sum('quantity')
        )['total_quantity'] or 0
        
        # Calculate available quantity
        context['available_quantity'] = product.stock_quantity - cart_items_quantity
        
        # Get cart item history
        context['cart_item_history'] = CartItem.history.filter(
            product=product
        ).order_by('-history_date')[:10]  # Last 10 transactions
        
        return context
    
    
    

# def mettre_a_jour_stock(product_id, new_quantity, operation='set'):
#     """
#     Met à jour la quantité d'un produit et son statut.
    
#     Args:
#         product_id (int): ID du produit à mettre à jour
#         new_quantity (int): Nouvelle quantité ou quantité à ajouter/soustraire
#         operation (str): Type d'opération ('set', 'add', 'subtract')
    
#     Returns:
#         tuple: (bool, str) - (succès de l'opération, message)
#     """
#     try:
#         from django.db import transaction
        
#         with transaction.atomic():
#             # Récupérer le produit
#             product = Product.objects.select_for_update().get(id=product_id)
            
#             # Calculer la nouvelle quantité selon l'opération
#             if operation == 'set':
#                 final_quantity = new_quantity
#             elif operation == 'add':
#                 final_quantity = product.stock_quantity + new_quantity
#             elif operation == 'subtract':
#                 final_quantity = product.stock_quantity - new_quantity
#             else:
#                 return False, "Opération non valide"
            
#             # Vérifier que la quantité n'est pas négative
#             if final_quantity < 0:
#                 return False, "La quantité ne peut pas être négative"
            
#             # Mettre à jour la quantité
#             product.stock_quantity = final_quantity
            
#             # Mettre à jour le statut selon la quantité
#             if final_quantity == 0:
#                 product.status = 'out_of_stock'
#             elif final_quantity > 0:
#                 product.status = 'available'
            
#             # Sauvegarder les modifications
#             product.save()
            
#             # Créer une entrée dans l'historique
#             product.history.create(
#                 history_date=timezone.now(),
#                 history_type="Mise à jour du stock",
#                 history_change_reason=f"Quantité modifiée de {product.stock_quantity} à {final_quantity}"
#             )
            
#             # Préparer le message de retour
#             status_message = "épuisé" if product.status == 'out_of_stock' else "disponible"
#             return True, f"Stock mis à jour. Nouvelle quantité: {final_quantity}, Statut: {status_message}"
            
#     except Product.DoesNotExist:
#         return False, "Produit non trouvé"
#     except Exception as e:
#         # Logger l'erreur pour le débogage
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.error(f"Erreur lors de la mise à jour du stock: {str(e)}")
#         return False, "Une erreur est survenue lors de la mise à jour"

# # Exemple d'utilisation dans une vue
# class UpdateProductStockView(LoginRequiredMixin, View):
#     def post(self, request, product_id):
#         try:
#             quantity = int(request.POST.get('quantity', 0))
#             operation = request.POST.get('operation', 'set')
            
#             success, message = mettre_a_jour_stock(product_id, quantity, operation)
            
#             if success:
#                 messages.success(request, message)
#             else:
#                 messages.error(request, message)
            
#             return redirect('product-detail', pk=product_id)
            
#         except ValueError:
#             messages.error(request, "Quantité invalide")
#             return redirect('product-detail', pk=product_id)
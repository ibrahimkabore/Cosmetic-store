from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.db.models import Sum, F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from e_commerce.forms import ProductForm
from e_commerce.models import CartItem, Product

class ProductsListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'stock/product_list.html'
    context_object_name = 'products'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate available quantity (stock - items in carts)
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
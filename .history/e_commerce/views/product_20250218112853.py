from django.views.generic import ListView
from django.db.models import Q
from e_commerce.models import CartItem, Product, Category, ParentCategory,Favorite

class ProductListView(ListView):
    model = Product
    template_name = 'home/product.html'
    context_object_name = 'products'
    paginate_by = 10  # Pagination  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add  category et category parent for flitred categories
        context['categories'] = Category.objects.all()
        context['parent_categories'] = ParentCategory.objects.all()
        context['number'] =CartItem.objects.count
     
        context['search_name'] = self.request.GET.get('search_name', '')
        context['category_id'] = self.request.GET.get('category', '')
        context['parent_category_id'] = self.request.GET.get('parent_category', '')
        # Gérer les favoris de l'utilisateur si l'utilisateur est authentifié
        user_favorites = []
        if self.request.user.is_authenticated:
            user_favorites = list(Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True))
            user_favorites = [str(id) for id in user_favorites]
        context['user_favorites'] = user_favorites
        return context

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Filtre par nom de produit
        search_name = self.request.GET.get('search_name')
        if search_name:
            queryset = queryset.filter(name__icontains=search_name)
        
        # Filtre par catégorie
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filtre par catégorie parente
        parent_category_id = self.request.GET.get('parent_category')
        if parent_category_id:
            queryset = queryset.filter(parent_id=parent_category_id)
            
        return queryset.order_by('name')
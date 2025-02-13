from django.views.generic import ListView
from django.db.models import Q
from e_commerce.models import Product, Category, ParentCategory,Favorite

from django.views.generic import ListView
 
class ProductListView(ListView):
    model = Product
    template_name = 'home/product.html'
    context_object_name = 'produits'
    paginate_by = 10  # Pagination des produits
    
    def get_context_data(self, **kwargs):
        # Récupérer le contexte par défaut
        context = super().get_context_data(**kwargs)

        # Récupérer les catégories et les catégories parentes pour les filtres
        context['categories'] = Category.objects.all()
        context['parent_categories'] = ParentCategory.objects.all()

        # Récupérer les paramètres de recherche
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
        # Récupérer tous les produits
        queryset = Product.objects.all()

        # Appliquer le filtre par nom de produit
        search_name = self.request.GET.get('search_name')
        if search_name:
            queryset = queryset.filter(name__icontains=search_name)

        # Appliquer le filtre par catégorie
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Appliquer le filtre par catégorie parente
        parent_category_id = self.request.GET.get('parent_category')
        if parent_category_id:
            queryset = queryset.filter(parent_id=parent_category_id)

        # Retourner les produits triés par nom
        return queryset.order_by('name')

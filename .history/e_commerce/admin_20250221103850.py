from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import *
from django.db.models import Sum
 
# Admin configuration for the Country model
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    # Columns to display in the countries list
    list_display = ('name', 'code', 'created_at')
    # Search fields for filtering countries
    search_fields = ('name', 'code')
    # Default sorting by name
    ordering = ('name',)
    # Number of items per page in the admin list view
    list_per_page = 20

# Admin configuration for the City model
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    # Columns to display in the cities list
    list_display = ('name', 'country', 'created_at')
    # Enable search by city name or country name
    search_fields = ('name', 'country__name')
    # Add a filter sidebar for countries
    list_filter = ('country',)
    # Sort by country first, then by city name
    ordering = ('country', 'name')
    list_per_page = 20

# Admin configuration for the CustomUser model
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Display key user information in the list view
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff' )
    # Enable search by username, email, and names
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # Add filters for staff status, active status, gender, and country
    list_filter = ('is_staff', 'is_active', 'gender' )
    # Organize fields into logical groups
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'gender')}),
        # (_('Location'), {'fields': ('country', 'city')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    list_per_page = 20

# Admin configuration for the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Display category hierarchy in the list view
    list_display = ('name', 'created_at')
    # Enable search by category name and description
    search_fields = ('name', 'description')
    
    ordering = ('name',)
    list_per_page = 20

@admin.register(ParentCategory)
class ParentCategoryAdmin(admin.ModelAdmin):
    # Display category hierarchy in the list view
    list_display = ('name','created_at')
    # Enable search by category name and description
    search_fields = ('name', 'description')
    # Add filter for parent categories
    
    ordering = ('name',)
    list_per_page = 20
    
# Admin configuration for the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'category',
        'parent', 
        'price', 
        'stock_quantity', 
        'status', 
        'bestseller', 
        'recommended'
    )
    search_fields = ('name', 'description', 'parent', 'category')
    list_filter = ('status', 'category', 'bestseller', 'recommended', 'parent', 'category')
    ordering = ('name',)
    list_editable = ('price', 'stock_quantity', 'status')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'category', 'parent', 'image')
        }),
        (_('Pricing and Stock'), {
            'fields': ('price', 'discount_percentage', 'stock_quantity')
        }),
        (_('Status and Features'), {
            'fields': ('status', 'bestseller', 'recommended', 'star_product')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if change:  # Si c'est une modification
            old_obj = self.model.objects.get(pk=obj.pk)
            stock_diff = obj.stock_quantity - old_obj.stock_quantity
            
            if stock_diff != 0:
                # Créer un mouvement de stock
                StockMovement.objects.create(
                    product=obj,
                    quantity=abs(stock_diff),
                    movement_type='IN' if stock_diff > 0 else 'OUT',
                    reason=_("Modification manuelle du stock"),
                    reference=f"ADMIN-{request.user.username}"
                )
        
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # Si c'est une modification
            readonly_fields.append('stock_quantity')  # Rendre stock_quantity en lecture seule
        return readonly_fields

    actions = ['add_stock', 'remove_stock']

    def add_stock(self, request, queryset):
        # Action pour ajouter du stock
        for product in queryset:
            StockMovement.objects.create(
                product=product,
                quantity=10,  # Quantité par défaut
                movement_type='IN',
                reason=_("Ajout de stock via action admin"),
                reference=f"ADMIN-{request.user.username}"
            )
    add_stock.short_description = _("Ajouter 10 unités au stock")

    def remove_stock(self, request, queryset):
        # Action pour retirer du stock
        for product in queryset:
            if product.stock_quantity >= 10:
                StockMovement.objects.create(
                    product=product,
                    quantity=10,  # Quantité par défaut
                    movement_type='OUT',
                    reason=_("Retrait de stock via action admin"),
                    reference=f"ADMIN-{request.user.username}"
                )
    remove_stock.short_description = _("Retirer 10 unités du stock")

# Admin configuration for the ShoppingCart model
@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    # Display cart status and ownership
    list_display = ('user', 'is_active', 'created_at')
    # Add filter for active/inactive carts
    list_filter = ('is_active',)
    # Enable search by username
    search_fields = ('user__username',)
    list_per_page = 20

 

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price', 'created_at')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('cart__is_active',)
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        obj.calculate_total_price()
        
        if not change:  # Si c'est une nouvelle création
            # Vérifier le stock disponible
            if obj.product.stock_quantity < obj.quantity:
                raise admin.ValidationError(_("Stock insuffisant pour ce produit"))
            
            # Créer le mouvement de stock
            StockMovement.objects.create(
                product=obj.product,
                quantity=obj.quantity,
                movement_type='OUT',
                reason=_("Ajout au panier via admin"),
                reference=f"ADMIN-CART-{obj.cart.id}"
            )
        
        elif change:  # Si c'est une modification
            old_obj = self.model.objects.get(pk=obj.pk)
            quantity_diff = obj.quantity - old_obj.quantity
            
            if quantity_diff != 0:
                if quantity_diff > 0 and obj.product.stock_quantity < quantity_diff:
                    raise admin.ValidationError(_("Stock insuffisant pour ce produit"))
                
                StockMovement.objects.create(
                    product=obj.product,
                    quantity=abs(quantity_diff),
                    movement_type='OUT' if quantity_diff > 0 else 'IN',
                    reason=_("Modification quantité panier via admin"),
                    reference=f"ADMIN-CART-{obj.cart.id}"
                )
        
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # Remettre le stock lors de la suppression
        StockMovement.objects.create(
            product=obj.product,
            quantity=obj.quantity,
            movement_type='IN',
            reason=_("Suppression du panier via admin"),
            reference=f"ADMIN-CART-{obj.cart.id}"
        )
        super().delete_model(request, obj)
 

# Admin configuration for the Review model
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # Show review information in the list view
    list_display = ('product', 'user', 'rating', 'recommended', 'review_date')
    # Enable search by product, username, and review content
    search_fields = ('product__name', 'user__username', 'comment')
    # Add filters for rating and recommendation status
    list_filter = ('rating', 'recommended', 'review_date')
    # Prevent modification of review date
    readonly_fields = ('review_date',)
    # Sort by most recent reviews first
    ordering = ('-review_date',)
    list_per_page = 20
    

@admin.register(Favorite)

class FavoriteAdmin(admin.ModelAdmin):
    pass

 
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Champs à afficher dans la liste
    list_display = (
        'ref', 
        'user', 
        'total', 
        'payment_method', 
        'status', 
        'payment_date', 
        'created_at', 
        'updated_at'
    )

    # Champs cliquables pour voir les détails
    list_display_links = ('ref', 'user')

    # Ajout de la recherche
    search_fields = ('ref', 'user__username', 'status')

    # Ajout de filtres
    list_filter = ('status', 'payment_method', 'created_at')

    # Permet de filtrer par période dans l'interface d'administration
    date_hierarchy = 'created_at'

    # Affichage des choix pour la méthode de paiement et le statut de la commande
    list_select_related = ('user',)

    # Ordonnancement personnalisé
    ordering = ['-created_at']

    # Exclusion de 'created_at' du formulaire
    exclude = ('created_at',)  # Exclure le champ 'created_at'

    # Ajouter des actions personnalisées si nécessaire
    actions = ['confirm_selected_payments']

    def confirm_selected_payments(self, request, queryset):
        """Action personnalisée pour confirmer le paiement des commandes sélectionnées."""
        count = queryset.update(status=Order.OrderStatus.PAYMENT_CONFIRMED, payment_date=timezone.now())
        self.message_user(request, f'{count} commandes ont été marquées comme Paiement Confirmé.')

    confirm_selected_payments.short_description = "Confirmer le paiement pour les commandes sélectionnées"

# Enregistrer le modèle dans l'interface d'administration
@admin.register(OrderLine)
    
class OrderLineAdmin(admin.ModelAdmin):
    # Champs à afficher dans la liste
    list_display = ('order', 'product', 'quantity', 'unit_price', 'line_total')
    
@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('date', 'product', 'movement_type', 'quantity', 'reason', 'reference')
    list_filter = ('movement_type', 'date', 'product__category')
    search_fields = ('product__name', 'reason', 'reference')
    date_hierarchy = 'date'
    readonly_fields = ('date',)
    ordering = ('-date',)
    list_per_page = 20

    fieldsets = (
        (_('Mouvement Information'), {
            'fields': ('product', 'movement_type', 'quantity')
        }),
        (_('Détails'), {
            'fields': ('reason', 'reference', 'date')
        }),
    )
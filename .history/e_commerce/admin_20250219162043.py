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
    # Show comprehensive product information in the list view
    list_display = ('name', 'category','parent', 'price', 'stock_quantity', 'status', 'bestseller', 'recommended')
    # Enable search by product name and description
    search_fields = ('name', 'description','parent','category')
    # Add filters for various product attributes
    list_filter = ('status', 'category', 'bestseller', 'recommended','parent','category')
    ordering = ('name',)
    # Allow direct editing of these fields in the list view
    list_editable = ('price', 'stock_quantity', 'status')
    # Prevent modification of timestamp fields
    readonly_fields = ('created_at', 'updated_at')
    # Organize product information into logical sections
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'category','parent','image')
        }),
        (_('Pricing and Stock'), {
            'fields': ('price', 'discount_percentage', 'stock_quantity')
        }),
        (_('Status and Features'), {
            'fields': ('status' , 'bestseller', 'recommended','star_product')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

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
    # Show item details in the list view, including total_price
    list_display = ('cart', 'product', 'quantity', 'total_price', 'created_at')

    # Enable search by username and product name
    search_fields = ('cart__user__username', 'product__name')

    # Filter by cart status
    list_filter = ('cart__is_active',)

    # Limit the number of items per page in the list view
    list_per_page = 20

    # You can call `calculate_total_price` when saving the object
    def save_model(self, request, obj, form, change):
        # Calculate the total price of the cart item before saving
        obj.calculate_total_price()
        
       
        
        # Proceed with saving the object
        super().save_model(request, obj, form, change)
 
 

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

 

from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'ref', 
        'user', 
        'total', 
        'payment_method', 
        'status', 
        'payment_date', 
 
         
    )

    # Fields that are clickable for detailed view
    list_display_links = ('ref', 'user')

    # Add search capability
    search_fields = ('ref', 'user__username', 'status')

    # Add filters
    list_filter = ('status', 'payment_method', 'created_at')

    # Allow filtering by date range in the admin interface
    date_hierarchy = 'created_at'

    # Display choices for payment method and order status
    list_select_related = ('user',)

    # Custom ordering                                                
    ordering = ['-created_at']

     

    # Optionally, you can add inline forms or actions
    actions = ['confirm_selected_payments']

    def confirm_selected_payments(self, request, queryset):
        """Custom action to confirm payment for selected orders."""
        count = queryset.update(status=Order.OrderStatus.PAYMENT_CONFIRMED, payment_date=timezone.now())
        self.message_user(request, f'{count} orders have been marked as Payment Confirmed.')

    confirm_selected_payments.short_description = "Confirm payment for selected orders"

# Register the model with the admin interface
admin.site.register(Order, OrderAdmin)

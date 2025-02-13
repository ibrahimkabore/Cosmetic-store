from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Country, City, CustomUser, Category, Product, 
    ShoppingCart, CartItem, Order, OrderItem, Review,ParentCategory
)

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
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'country', 'city')
    # Enable search by username, email, and names
    search_fields = ('username', 'email', 'first_name', 'last_name')
    # Add filters for staff status, active status, gender, and country
    list_filter = ('is_staff', 'is_active', 'gender', 'country')
    # Organize fields into logical groups
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'gender')}),
        (_('Location'), {'fields': ('country', 'city')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    list_per_page = 20

# Admin configuration for the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Display category hierarchy in the list view
    list_display = ('name', 'parent', 'created_at')
    # Enable search by category name and description
    search_fields = ('name')
    # Add filter for parent categories
    list_filter = ('parent',)
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
    list_display = ('name', 'category', 'price', 'stock_quantity', 'status', 'favorite', 'bestseller', 'recommended')
    # Enable search by product name and description
    search_fields = ('name', 'description')
    # Add filters for various product attributes
    list_filter = ('status', 'category', 'favorite', 'bestseller', 'recommended')
    ordering = ('name',)
    # Allow direct editing of these fields in the list view
    list_editable = ('price', 'stock_quantity', 'status')
    # Prevent modification of timestamp fields
    readonly_fields = ('created_at', 'updated_at')
    # Organize product information into logical sections
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'category', 'image')
        }),
        (_('Pricing and Stock'), {
            'fields': ('price', 'discount_percentage', 'stock_quantity')
        }),
        (_('Status and Features'), {
            'fields': ('status', 'favorite', 'bestseller', 'recommended')
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

# Admin configuration for the CartItem model
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    # Show item details in the list view
    list_display = ('cart', 'product', 'quantity', 'created_at')
    # Enable search by username and product name
    search_fields = ('cart__user__username', 'product__name')
    # Filter by cart status
    list_filter = ('cart__is_active',)
    list_per_page = 20

# Admin configuration for the Order model
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Display order summary in the list view
    list_display = ('user', 'status', 'total_price', 'created_at')
    # Enable search by username and shipping address
    search_fields = ('user__username', 'shipping_address')
    # Add filter for order status
    list_filter = ('status',)
    # Prevent modification of timestamp fields
    readonly_fields = ('created_at', 'updated_at')
    # Organize order information into sections
    fieldsets = (
        (_('Order Information'), {
            'fields': ('user', 'status', 'total_price')
        }),
        (_('Shipping Details'), {
            'fields': ('shipping_address',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

# Admin configuration for the OrderItem model
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # Display order item details
    list_display = ('order', 'product', 'quantity', 'price_at_purchase')
    # Enable search by username and product name
    search_fields = ('order__user__username', 'product__name')
    # Filter by order status
    list_filter = ('order__status',)
    list_per_page = 20

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
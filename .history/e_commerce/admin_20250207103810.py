from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Country, City, CustomUser, Category, Product, 
    ShoppingCart, CartItem, Order, OrderItem, Review
)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    ordering = ('name',)
    list_per_page = 20

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'created_at')
    search_fields = ('name', 'country__name')
    list_filter = ('country',)
    ordering = ('country', 'name')
    list_per_page = 20

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'country', 'city')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'gender', 'country')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'gender')}),
        (_('Location'), {'fields': ('country', 'city')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    list_per_page = 20

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('parent',)
    ordering = ('name',)
    list_per_page = 20

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'status', 'favorite', 'bestseller', 'recommended')
    search_fields = ('name', 'description')
    list_filter = ('status', 'category', 'favorite', 'bestseller', 'recommended')
    ordering = ('name',)
    list_editable = ('price', 'stock_quantity', 'status')
    readonly_fields = ('created_at', 'updated_at')
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

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username',)
    list_per_page = 20

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'created_at')
    search_fields = ('cart__user__username', 'product__name')
    list_filter = ('cart__is_active',)
    list_per_page = 20

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_price', 'created_at')
    search_fields = ('user__username', 'shipping_address')
    list_filter = ('status',)
    readonly_fields = ('created_at', 'updated_at')
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

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price_at_purchase')
    search_fields = ('order__user__username', 'product__name')
    list_filter = ('order__status',)
    list_per_page = 20

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'recommended', 'review_date')
    search_fields = ('product__name', 'user__username', 'comment')
    list_filter = ('rating', 'recommended', 'review_date')
    readonly_fields = ('review_date',)
    ordering = ('-review_date',)
    list_per_page = 20
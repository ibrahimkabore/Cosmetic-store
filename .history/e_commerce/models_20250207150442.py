from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
import uuid
import os
from simple_history.models import HistoricalRecords
from django.contrib.auth.signals import user_logged_in, user_logged_out

##### models  base #####
class BaseModel(SafeDeleteModel):
    
    """
    Abstract base model that provides common fields for all other models, including:
    - `id`: A unique UUID identifier for the model instance.
    - `created_at`: Timestamp for the creation of the record.
    - `updated_at`: Timestamp for the last update of the record.
    - Soft delete functionality using SafeDelete with cascade deletion.
    """
    
    id = models.UUIDField(
        _("Unique Identifier"), 
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    created_at = models.DateTimeField(
        _("Creation Timestamp"), 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("Last Update Timestamp"), 
        auto_now=True
    )
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        abstract = True

##### models contry ####
class Country(BaseModel):
    
    """
    Model representing a country.
    - `name`: Unique name of the country (e.g., "France").
    - `code`: ISO code of the country (maximum 3 characters).
    - Historical tracking enabled to maintain change logs.
    """
    name = models.CharField(
        _("Country Name"), 
        max_length=100, 
        unique=True
    )
    code = models.CharField(
        _("Country Code"), 
        max_length=3, 
        unique=True
    )
    
    history = HistoricalRecords(
        table_name='Contry_history', 
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )

    def __str__(self):
        return self.name

#### models City ########
class City(BaseModel):
    """
    Model representing a city.
    - `name`: Name of the city.
    - `country`: Foreign key to associate the city with a specific country.
    - Unique constraint to ensure no duplicate city-country combinations.
    - Historical tracking enabled for change logs.
    """
    name = models.CharField(
        _("City Name"), 
        max_length=100
    )
    country = models.ForeignKey(
        Country, 
        on_delete=models.CASCADE, 
        related_name='cities',
        verbose_name=_("Associated Country")
    )
    
    class Meta:
        unique_together = ['name', 'country']
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
    
    history = HistoricalRecords(table_name='City_history', history_id_field=models.UUIDField(default=uuid.uuid4))

    def __str__(self):
        return f"{self.name}, {self.country.name}"

#### models User  personaliser ########
class CustomUser(AbstractUser, BaseModel):
    
    """
    Customized user model inheriting from Django's AbstractUser.
    - `phone`: User's phone number.
    - `gender`: Gender with predefined choices (Male, Female, Other).
    - `country`: Associated country of the user (optional).
    - `city`: Associated city of the user (optional).
    - History tracking and login/logout signals to manage online status.
    """
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other'))
    ]

    phone = models.CharField(
        _("Phone Number"), 
        max_length=15, 
        blank=True
    )
    gender = models.CharField(
        _("Gender"), 
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True
    )
    country = models.ForeignKey(
        Country, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_("User Country")
    )
    city = models.ForeignKey(
        City, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_("User City")
    )
    
    # Ajout de related_name pour éviter les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return f"{self.username}"

    # Signaux pour mettre à jour le statut en ligne et la date de dernière connexion
    @receiver(user_logged_in)
    def user_logged_in_handler(sender, request, user, **kwargs):
        user.is_online = True
        user.last_login = timezone.now()  # Met à jour le champ last_login
        user.save()

    @receiver(user_logged_out)
    def user_logged_out_handler(sender, request, user, **kwargs):
        user.is_online = False
        user.save()
    
    
    history = HistoricalRecords(table_name='CustomUser_history', history_id_field=models.UUIDField(default=uuid.uuid4))

# ####### MODEL PARENTCATEGORY ########
# class ParentCategory(BaseModel):
    
#     """
#     Model representing a parent category for product categorization.
#     - `name`: Unique name of the parent category.
#     - `description`: Optional description of the parent category.
#     - Historical tracking enabled for change logs.
#     """
    
#     name = models.CharField(
#         _("Parent Category Name"),
#         max_length=100,
#         unique=True
#     )
#     description = models.TextField(
#         _("Parent Category Description"),
#         blank=True
#     )
#     history = HistoricalRecords(
#         table_name='ParentCategory_history',
#         history_id_field=models.UUIDField(default=uuid.uuid4)
#     )

#     class Meta:
#         verbose_name = _("Parent Category")
#         verbose_name_plural = _("Parent Categories")
#         ordering = ['name']

#     def __str__(self):
#         return self.name

###### Model CATEGORY#####
class Category(BaseModel):
    """
    Model representing a category, potentially linked to a parent category.
    - `name`: Unique name of the category.
    - `parent`: Optional foreign key linking to a ParentCategory.
    - Historical tracking enabled for change logs.
    """

    name = models.CharField(
        _("Category Name"),
        max_length=100,
        unique=False
    )
    
    # parent = models.ForeignKey(
    #     ParentCategory,
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name='categories',
    #     verbose_name=_("Parent Category")
    # )
    history = HistoricalRecords(
        table_name='Category_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return f"{self.name} "

# models Product ########
class Product(BaseModel):
    
    """
    Model representing a product with detailed attributes.
    - `name`: Unique name of the product.
    - `description`: Description of the product.
    - `category`: Foreign key linking the product to a specific category.
    - `price`: Product price with minimum validation.
    - `discount_percentage`: Optional discount on the product.
    - `stock_quantity`: Available stock count.
    - `status`: Availability status (available, out_of_stock, discontinued).
    - `image`: Optional image of the product.
    - `favorite`, `bestseller`, `recommended`: Flags for product categorization.
    """
    
    STATUS_CHOICES = [
        ('available', _('Available')),
        ('out_of_stock', _('Out of Stock')),
        ('discontinued', _('Discontinued'))
    ]

    name = models.CharField(
        _("Product Name"), 
        max_length=200, 
        unique=True
    )
    description = models.TextField(
        _("Product Description")
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name=_("Product Category")
    )
    
    price = models.DecimalField(
        _("Product Price"), 
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    discount_percentage = models.DecimalField(
        _("Discount Percentage"), 
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, 
        blank=True
    )
    
    stock_quantity = models.PositiveIntegerField(
        _("Stock Quantity"), 
        default=0
    )
    status = models.CharField(
        _("Product Status"), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available'
    )
    
    image = models.ImageField(
        _("Product Image"), 
        upload_to='products/', 
        null=True, 
        blank=True
    )
    
    # Dropdown list to check if the product is a favorite
    FAVORITE_CHOICES = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]
    
    favorite = models.CharField(
        max_length=3,
        choices=FAVORITE_CHOICES,
        default='No',  # By default, the product is not marked as a favorite
        verbose_name='Is the product a favorite?'
    )
    
    # Dropdown list to check if the product is a best seller
    BESTSELLER_CHOICES = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]
    
    bestseller = models.CharField(
        max_length=3,
        choices=BESTSELLER_CHOICES,
        default='No',  # By default, the product is not a best seller
        verbose_name='Is the product a best seller?'
    )
    
    # Dropdown list to check if the product is recommended
    RECOMMENDED_CHOICES = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]
    
    recommended = models.CharField(
        max_length=3,
        choices=RECOMMENDED_CHOICES,
        default='No',  # By default, the product is not recommended
        verbose_name='Is the product recommended?'
    )
    
    history = HistoricalRecords(table_name='Product_history', history_id_field=models.UUIDField(default=uuid.uuid4))

##### models Shopping Cart ########
class ShoppingCart(BaseModel):
    
    """
    Model representing a shopping cart for a user.
    - `user`: Foreign key linking the cart to a specific user.
    - `is_active`: Status indicating whether the cart is active.
    """
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        verbose_name=_("Cart Owner")
    )
    is_active = models.BooleanField(
        _("Cart Active Status"), 
        default=True
    )
    
    history = HistoricalRecords(table_name='ShoppingCart_history', history_id_field=models.UUIDField(default=uuid.uuid4))

######### models cartItem #########
class CartItem(BaseModel):
    
    """
    Model representing an item within a shopping cart.
    - `cart`: Foreign key linking the item to a specific shopping cart.
    - `product`: Foreign key linking the item to a specific product.
    - `quantity`: Quantity of the product within the cart.
    """
    
    cart = models.ForeignKey(
        ShoppingCart, 
        related_name='cart_items', 
        on_delete=models.CASCADE,
        verbose_name=_("Shopping Cart")
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name=_("Product")
    )
    quantity = models.PositiveIntegerField(
        _("Product Quantity"), 
        default=1
    )

    history = HistoricalRecords(table_name='CartItem_history', history_id_field=models.UUIDField(default=uuid.uuid4))

###### model oder   ######
class Order(BaseModel):
    
    """
    Model representing an order placed by a user.
    - `user`: Foreign key linking the order to a specific customer.
    - `status`: Order status (pending, processing, shipped, delivered, cancelled).
    - `total_price`: Total price of the order.
    - `shipping_address`: Address for order delivery.
    """
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled'))
    ]

    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        verbose_name=_("Order Customer")
    )
    status = models.CharField(
        _("Order Status"), 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    total_price = models.DecimalField(
        _("Total Order Price"), 
        max_digits=10, 
        decimal_places=2
    )
    shipping_address = models.TextField(
        _("Shipping Address")
    )
    
    history = HistoricalRecords(table_name='Order_history', history_id_field=models.UUIDField(default=uuid.uuid4))

###### model oderItem   ######
class OrderItem(BaseModel):
    
    """
    Model representing an item in an order.

    - `order`: ForeignKey linking the item to a specific order. 
    - `product`: ForeignKey linking the item to a specific product.
    - `quantity`: The number of products ordered.
    - `price_at_purchase`: The price of the product at the time of purchase.
    - `history`: Historical record for tracking changes to the OrderItem model.
    """
    
    order = models.ForeignKey(
        Order, 
        related_name='items', 
        on_delete=models.CASCADE,
        verbose_name=_("Associated Order")
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        verbose_name=_("Ordered Product")
    )
    quantity = models.PositiveIntegerField(
        _("Product Quantity")
    )
    price_at_purchase = models.DecimalField(
        _("Product Price at Purchase"), 
        max_digits=10, 
        decimal_places=2
    )
    
    history = HistoricalRecords(table_name='OrderItem_history', history_id_field=models.UUIDField(default=uuid.uuid4))
    
###### model Reviews   ######   
class Review(BaseModel):
    
    """
    Model representing a review for a product.

    - `product`: ForeignKey linking the review to a specific product.
    - `user`: ForeignKey linking the review to the user who created it.
    - `rating`: Rating given by the user (from 1 to 5).
    - `comment`: Optional comment provided by the user.
    - `review_date`: Timestamp indicating when the review was posted.
    - `recommended`: Whether the user recommends the product or not (neutral, recommended, or not recommended).
    - `history`: Historical record for tracking changes to the Review model.
    """
    
    RATING_CHOICES = [
        (1, _('1 - Very Unsatisfied')),
        (2, _('2 - Unsatisfied')),
        (3, _('3 - Average')),
        (4, _('4 - Satisfied')),
        (5, _('5 - Excellent'))
    ]

    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("Associated Product")
    )
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    rating = models.IntegerField(
        _("Rating"), 
        choices=RATING_CHOICES
    )
    comment = models.TextField(
        _("Comment"),
        max_length=1000,
        blank=True
    )
    review_date = models.DateTimeField(
        _("Review Date"),
        auto_now_add=True
    )
    RECOMMENDATION_CHOICES = [
    ('not_recommended', _('Not Recommended')),
    ('neutral', _('Neutral')),
    ('recommended', _('Recommended'))
    ]

    recommended = models.CharField(
        _("Recommendation Status"),
        max_length=20,
        choices=RECOMMENDATION_CHOICES,
        default='neutral'
    )

    history = HistoricalRecords(table_name='Review_history', history_id_field=models.UUIDField(default=uuid.uuid4))
    class Meta:
        unique_together = ['product', 'user']
    
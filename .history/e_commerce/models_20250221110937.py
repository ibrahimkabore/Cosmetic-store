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
from django.db.models import Sum
from simple_history.models import HistoricalRecords
from django.contrib.auth.signals import user_logged_in, user_logged_out
import pyotp
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
class CustomUser(AbstractUser, SafeDeleteModel):
    
    """
    Customized user model inheriting from Django's AbstractUser.
    - `phone`: User's phone number.
    - `gender`: Gender with predefined choices (Male, Female, Other).
    - `country`: Associated country of the user (optional).
    - `city`: Associated city of the user (optional).
    - History tracking and login/logout signals to manage online status.
    """
    GENDER_CHOICES = [
        ('H', _('Homme')),
        ('F', _('Femme')),
        ('A', _('Autre'))
    ]

    TYPES_USER = [
        ('C', _('Client')),
        ('G', _('Gestionnaire')),
        ('A', _('Administrateur'))
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
    
    type_user = models.CharField(
        _("type user"), 
        max_length=1, 
        choices=TYPES_USER, 
        blank=True,
        default='C'  # Default value set to 'C' for Client
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
    
    country = models.ForeignKey(
        Country, 
        on_delete=models.SET_NULL, 
        null=True,  # Makes the field optional
        blank=True,  # Allows the field to be left empty in forms
        verbose_name=_("User Country")
    )
    
    city = models.ForeignKey(
        City, 
        on_delete=models.SET_NULL, 
        null=True,  # Makes the field optional
        blank=True,  # Allows the field to be left empty in forms
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
    is_verified = models.BooleanField(default=False)
    
    is_online = models.BooleanField(default=False)  # champ pour le statut en ligne
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='personnel_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='personnel_permissions_set',  # Ajoutez un related_name unique
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    history = HistoricalRecords(table_name='CustomUser_history', history_id_field=models.UUIDField(default=uuid.uuid4))

    
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
        
     # New fields for two-factor authentication
    two_factor_method = models.CharField(
        max_length=20, 
        choices=[
            ('email', 'Email Code'),
            ('google_auth', 'Google Authenticator')
        ],
        null=True,
        blank=True
    )
    google_auth_secret = models.CharField(max_length=32, null=True, blank=True)
    
    def generate_google_auth_secret(self):
        if not self.google_auth_secret:
            self.google_auth_secret = pyotp.random_base32()
            self.save()
        return self.google_auth_secret
    
    def verify_google_auth_code(self, code):
        if not self.google_auth_secret:
            return False
        totp = pyotp.TOTP(self.google_auth_secret)
        return totp.verify(code)
    
    def __str__(self):
        return f"{self.username}"

        
####### MODEL PARENTCATEGORY ########
class ParentCategory(BaseModel):
    
    """
    Model representing a parent category for product categorization.
    - `name`: Unique name of the parent category.
    - `description`: Optional description of the parent category.
    - Historical tracking enabled for change logs.
    """
    
    name = models.CharField(
        _("Teint Category Name"),
        max_length=100,
        unique=True
    )
     
    history = HistoricalRecords(
        table_name='ParentCategory_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )

    class Meta:
        verbose_name = _("Parent Category")
        verbose_name_plural = _("Parent Categories")
        ordering = ['name']

    def __str__(self):
        return self.name

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
        unique=True
    )
    
    history = HistoricalRecords(
        table_name='Category_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def __str__(self):
        return f"{self.name}  "


class VerificationCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    

 
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
        verbose_name=_(" Category")
    )
    parent = models.ForeignKey(
        ParentCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='categories',
        verbose_name=_("Teint Category")
    )
    
    price = models.DecimalField(
        _("Product Price"), 
        max_digits=10, 
        decimal_places=0, 
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
    
   # Choices for star product status
    STAR_PRODUCT_CHOICES = [
        ('No', 'No'),
        ('Yes', 'Yes'),
    ]

    star_product = models.CharField(
        max_length=3,
        choices=STAR_PRODUCT_CHOICES,
        default='No',  # By default, the product is not a star product
        verbose_name='Is this a star product?'
    )
    
    history = HistoricalRecords(table_name='Product_history', history_id_field=models.UUIDField(default=uuid.uuid4))
    
    def __str__(self):
        return self.name
    
    def add_stock(self, quantity):
        """
        Ajoute du stock au produit
        """
        if quantity < 0:
            raise ValueError(_("La quantité doit être positive"))
        
        self.stock_quantity += quantity
        
        if self.stock_quantity > 0 and self.status == 'out_of_stock':
            self.status = 'available'
        
        self.save(update_fields=['stock_quantity', 'status'])

    def remove_stock(self, quantity):
        """
        Retire du stock du produit
        """
        if quantity < 0:
            raise ValueError(_("La quantité doit être positive"))
        
        if quantity > self.stock_quantity:
            raise ValueError(_("Stock insuffisant"))
        
        self.stock_quantity -= quantity
        
        if self.stock_quantity == 0:
            self.status = 'out_of_stock'
        
        self.save(update_fields=['stock_quantity', 'status'])

    def get_stock_movements(self, start_date=None, end_date=None):
        """
        Récupère l'historique des mouvements de stock
        """
        movements = self.stock_movements.all()
        
        if start_date:
            movements = movements.filter(date__gte=start_date)
        if end_date:
            movements = movements.filter(date__lte=end_date)
            
        return movements.order_by('-date')


# Ajout des choix pour le type de mouvement
class StockMovement(BaseModel):
    """
    Modèle pour tracer tous les mouvements de stock (entrées et sorties)
    """
    MOVEMENT_TYPES = [
        ('IN', _('Entrée')),
        ('OUT', _('Sortie'))
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements',
        verbose_name=_("Produit")
    )
    
    quantity = models.PositiveIntegerField(
        _("Quantité"),
        validators=[MinValueValidator(1)]
    )
    
    movement_type = models.CharField(
        _("Type de mouvement"),
        max_length=3,
        choices=MOVEMENT_TYPES
    )
    
    reason = models.CharField(
        _("Motif"),
        max_length=200,
        help_text=_("Raison du mouvement de stock (ex: réapprovisionnement, vente, retour, etc.)")
    )
    
    date = models.DateTimeField(
        _("Date du mouvement"),
        auto_now_add=True
    )
    
    reference = models.CharField(
        _("Référence"),
        max_length=50,
        blank=True,
        help_text=_("Numéro de commande, bon de livraison, etc.")
    )

    history = HistoricalRecords(
        table_name='StockMovement_history',
        history_id_field=models.UUIDField(default=uuid.uuid4)
    )

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if not self.pk:  # Si c'est un nouveau mouvement
            if self.movement_type == 'IN':
                self.product.add_stock(self.quantity)
            elif self.movement_type == 'OUT':
                self.product.remove_stock(self.quantity)
        super().save(*args, **kwargs)
    
class Favorite(models.Model):
    """
    Model representing user's favorite products
    """
    
    id = models.UUIDField(
        _("Unique Identifier"), 
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    
    created_at = models.DateTimeField(
        _("Creation Timestamp"), 
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("Last Update Timestamp"), 
        auto_now=True
    )

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
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
    
    def __str__(self):
        return f"{self.user.username}'s Shopping Cart"

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

    total_price = models.DecimalField(max_digits=10, decimal_places=0,default=1)  # adjust values as needed
    
   
    
    history = HistoricalRecords(table_name='CartItem_history', history_id_field=models.UUIDField(default=uuid.uuid4))
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def calculate_total_price(self):
        """Calcule le prix total pour cet article du panier."""
        self.total_price = self.product.price * self.quantity
        self.save(update_fields=['total_price'])  # Optimisation : Met à jour uniquement ce champ

    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour gérer le stock lors de l'ajout au panier
        """
        try:
            if not self.pk:  # Si c'est un nouvel article dans le panier
                # Vérifier si le stock est suffisant
                if self.product.stock_quantity < self.quantity:
                    raise ValueError(_("Stock insuffisant pour ce produit"))
                
                # Créer le mouvement de stock
                StockMovement.objects.create(
                    product=self.product,
                    quantity=self.quantity,
                    movement_type='OUT',
                    reason="Ajout au panier",
                    reference=f"CART-{self.cart.id}"
                )
            
            elif self.pk:  # Si c'est une modification d'un article existant
                try:
                    # Récupérer l'ancien article pour comparer les quantités
                    old_item = CartItem.objects.get(pk=self.pk)
                    quantity_diff = self.quantity - old_item.quantity
                    
                    if quantity_diff > 0:  # Si la quantité a augmenté
                        if self.product.stock_quantity < quantity_diff:
                            raise ValueError(_("Stock insuffisant pour ce produit"))
                        
                        # Créer un mouvement de stock pour la différence
                        StockMovement.objects.create(
                            product=self.product,
                            quantity=quantity_diff,
                            movement_type='OUT',
                            reason="Modification quantité panier",
                            reference=f"CART-{self.cart.id}"
                        )
                    elif quantity_diff < 0:  # Si la quantité a diminué
                        # Créer un mouvement de stock pour remettre en stock
                        StockMovement.objects.create(
                            product=self.product,
                            quantity=abs(quantity_diff),
                            movement_type='IN',
                            reason="Modification quantité panier",
                            reference=f"CART-{self.cart.id}"
                        )
                except CartItem.DoesNotExist:
                    # Si l'item n'existe pas encore, le traiter comme un nouvel item
                    if self.product.stock_quantity < self.quantity:
                        raise ValueError(_("Stock insuffisant pour ce produit"))
                    
                    StockMovement.objects.create(
                        product=self.product,
                        quantity=self.quantity,
                        movement_type='OUT',
                        reason="Ajout au panier",
                        reference=f"CART-{self.cart.id}"
                    )

            # Calculer le prix total
            self.total_price = self.product.price * self.quantity
            super().save(*args, **kwargs)
        except Exception as e:
            print(f"Erreur dans save() de CartItem: {type(e).__name__} - {str(e)}")
            raise
    def delete(self, *args, **kwargs):
        """
        Surcharge de la méthode delete pour remettre en stock lors de la suppression
        """
        # Remettre la quantité en stock
        StockMovement.objects.create(
            product=self.product,
            quantity=self.quantity,
            movement_type='IN',
            reason="Suppression du panier",
            reference=f"CART-{self.cart.id}"
        )
        
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Order(BaseModel):
    # Payment method choices
    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = 'CB', 'Carte Bancaire'
        MOBILE_MONEY = 'MM', 'Mobile Money'

        CASH = 'CS', 'Cash'

    # Order status choices
    class OrderStatus(models.TextChoices):
        PENDING =  'EA', 'En attente de paiement'
        PAYMENT_CONFIRMED = 'PC', 'Paiement confirmé'
        PROCESSING = 'EP', 'En préparation'
        SHIPPED ='EX', 'Expédié'
        DELIVERED = 'LV', 'Livré'
        CANCELLED = 'AN', 'Annulé'
        REFUNDED =  'RB', 'Remboursé'

    ref = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Référence")
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    total = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    # Payment and status fields
    payment_method = models.CharField(
        max_length=2,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CREDIT_CARD,
        verbose_name="Payment Method"
    )

    status = models.CharField(
        max_length=2,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="Order Status"
    )

    payment_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Payment Date"
    )
 
    def __str__(self):
        return f"Order {self.ref} - {self.user.username} - {self.get_status_display()}"

    def confirm_payment(self):
        """Confirm order payment"""
        self.status = self.OrderStatus.PAYMENT_CONFIRMED
        self.payment_date = timezone.now()
        self.save()

    def mark_as_processing(self):
        """Change status to 'Processing'"""
        self.status = self.OrderStatus.PROCESSING
        self.save()

    def mark_as_shipped(self):
        """Change status to 'Shipped'"""
        self.status = self.OrderStatus.SHIPPED
        self.save()

    def mark_as_delivered(self):
        """Change status to 'Delivered'"""
        self.status = self.OrderStatus.DELIVERED
        self.save()

    def cancel(self):
        """Cancel the order"""
        self.status = self.OrderStatus.CANCELLED
        self.save()

    def refund(self):
        """Refund the order"""
        self.status = self.OrderStatus.REFUNDED
        self.save()
        
    def save(self, *args, **kwargs):
        if not self.ref:
            # Générer une référence unique basée sur un UUID
            self.ref = f'DC-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

  

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
    
    
class OrderLine(models.Model):
    order = models.ForeignKey(Order, related_name='lines', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)
    line_total = models.DecimalField(max_digits=10, decimal_places=0)
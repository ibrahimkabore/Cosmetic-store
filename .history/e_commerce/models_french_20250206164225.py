from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
import uuid
import os

class ModeleDeBase(SafeDeleteModel):
    id = models.UUIDField(
        _("Identifiant Unique"), 
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    date_creation = models.DateTimeField(
        _("Horodatage de Création"), 
        auto_now_add=True
    )
    date_mise_a_jour = models.DateTimeField(
        _("Horodatage de Dernière Mise à Jour"), 
        auto_now=True
    )
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        abstract = True

class Pays(ModeleDeBase):
    nom = models.CharField(
        _("Nom du Pays"), 
        max_length=100, 
        unique=True
    )
    code = models.CharField(
        _("Code du Pays"), 
        max_length=3, 
        unique=True
    )
    
    def __str__(self):
        return self.nom

class Ville(ModeleDeBase):
    nom = models.CharField(
        _("Nom de la Ville"), 
        max_length=100
    )
    pays = models.ForeignKey(
        Pays, 
        on_delete=models.CASCADE, 
        related_name='villes',
        verbose_name=_("Pays Associé")
    )
    
    class Meta:
        unique_together = ['nom', 'pays']
        verbose_name = _("Ville")
        verbose_name_plural = _("Villes")
    
    def __str__(self):
        return f"{self.nom}, {self.pays.nom}"

class UtilisateurPersonnalise(AbstractUser, ModeleDeBase):
    CHOIX_GENRE = [
        ('M', _('Masculin')),
        ('F', _('Féminin')),
        ('A', _('Autre'))
    ]

    telephone = models.CharField(
        _("Numéro de Téléphone"), 
        max_length=15, 
        blank=True
    )
    genre = models.CharField(
        _("Genre"), 
        max_length=1, 
        choices=CHOIX_GENRE, 
        blank=True
    )
    pays = models.ForeignKey(
        Pays, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_("Pays de l'Utilisateur")
    )
    ville = models.ForeignKey(
        Ville, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_("Ville de l'Utilisateur")
    )
    
    est_connecte = models.BooleanField(
        _("Statut de Connexion"), 
        default=False
    )
    derniere_activite = models.DateTimeField(
        _("Horodatage de Dernière Activité"), 
        null=True, 
        blank=True
    )

class Categorie(ModeleDeBase):
    nom = models.CharField(
        _("Nom de la Catégorie"), 
        max_length=100, 
        unique=True
    )
    description = models.TextField(
        _("Description de la Catégorie"), 
        blank=True
    )
    categorie_parente = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='sous_categories',
        verbose_name=_("Catégorie Parente")
    )

    def __str__(self):
        return self.nom

class Produit(ModeleDeBase):
    STATUTS_PRODUIT = [
        ('disponible', _('Disponible')),
        ('rupture', _('Rupture de Stock')),
        ('arrete', _('Arrêté'))
    ]

    nom = models.CharField(
        _("Nom du Produit"), 
        max_length=200, 
        unique=True
    )
    description = models.TextField(
        _("Description du Produit")
    )
    categorie = models.ForeignKey(
        Categorie, 
        on_delete=models.CASCADE, 
        related_name='produits',
        verbose_name=_("Catégorie du Produit")
    )
    
    prix = models.DecimalField(
        _("Prix du Produit"), 
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    pourcentage_reduction = models.DecimalField(
        _("Pourcentage de Réduction"), 
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, 
        blank=True
    )
    
    quantite_stock = models.PositiveIntegerField(
        _("Quantité en Stock"), 
        default=0
    )
    statut = models.CharField(
        _("Statut du Produit"), 
        max_length=20, 
        choices=STATUTS_PRODUIT, 
        default='disponible'
    )
    
    image = models.ImageField(
        _("Image du Produit"), 
        upload_to='produits/', 
        null=True, 
        blank=True
    )

class PanierAchats(ModeleDeBase):
    utilisateur = models.ForeignKey(
        UtilisateurPersonnalise, 
        on_delete=models.CASCADE,
        verbose_name=_("Propriétaire du Panier")
    )
    est_actif = models.BooleanField(
        _("Statut Actif du Panier"), 
        default=True
    )

class ArticlePanier(ModeleDeBase):
    panier = models.ForeignKey(
        PanierAchats, 
        related_name='articles_panier', 
        on_delete=models.CASCADE,
        verbose_name=_("Panier d'Achat")
    )
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE,
        verbose_name=_("Produit")
    )
    quantite = models.PositiveIntegerField(
        _("Quantité de Produit"), 
        default=1
    )

class Commande(ModeleDeBase):
    STATUTS_COMMANDE = [
        ('en_attente', _('En Attente')),
        ('en_cours', _('En Cours')),
        ('expedie', _('Expédié')),
        ('livre', _('Livré')),
        ('annule', _('Annulé'))
    ]

    utilisateur = models.ForeignKey(
        UtilisateurPersonnalise, 
        on_delete=models.CASCADE,
        verbose_name=_("Client de la Commande")
    )
    statut = models.CharField(
        _("Statut de la Commande"), 
        max_length=20, 
        choices=STATUTS_COMMANDE, 
        default='en_attente'
    )
    prix_total = models.DecimalField(
        _("Prix Total de la Commande"), 
        max_digits=10, 
        decimal_places=2
    )
    adresse_livraison = models.TextField(
        _("Adresse de Livraison")
    )

class ArticleCommande(ModeleDeBase):
    commande = models.ForeignKey(
        Commande, 
        related_name='articles', 
        on_delete=models.CASCADE,
        verbose_name=_("Commande Associée")
    )
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE,
        verbose_name=_("Produit Commandé")
    )
    quantite = models.PositiveIntegerField(
        _("Quantité de Produit")
    )
    prix_achat = models.DecimalField(
        _("Prix du Produit à l'Achat"), 
        max_digits=10, 
        decimal_places=2
    )
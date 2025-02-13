from django.db import models
from safedelete.models import SafeDeleteModel, SOFT_DELETE_CASCADE
from django.contrib.auth.models import AbstractUser
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os.path
import os
import uuid
from django.utils import timezone
import random
from django_lifecycle import LifecycleModel
from io import BytesIO
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError


imageFs = FileSystemStorage(location=os.path.join(str(settings.BASE_DIR),
                                                '/medias/'))

####     models contry ########
class Contry(SafeDeleteModel,LifecycleModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(max_length=50)
    history = HistoricalRecords(table_name='Contry_history', history_id_field=models.UUIDField(default=uuid.uuid4))

    def __str__(self):
        return self.name

##     models city ########
class City(SafeDeleteModel,LifecycleModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(max_length=50)
    contry = models.ForeignKey(Contry, on_delete=models.CASCADE)
    history = HistoricalRecords(table_name='City_history', history_id_field=models.UUIDField(default=uuid.uuid4))

    def __str__(self):
        return self.name

####     models CustomUsers ########
class CustomUsers(AbstractUser,SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    contry = models.ForeignKey(Contry, on_delete=models)
    city=models.ForeignKey(City, on_delete=models.CASCADE)
    contact = models.CharField(max_length=10)
    account_creation_date = models.DateTimeField(default=timezone.now, editable=False)
    is_online = models.BooleanField(default=False)
    
    
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
    
    

####     models Verificade Code ########
class VerificationCode(models.Model):
    _safedelete_policy = SOFT_DELETE_CASCADE

    user = models.OneToOneField(CustomUsers, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"

##### models Category ########
class Category (SafeDeleteModel,LifecycleModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    history = HistoricalRecords(table_name='Category_history', history_id_field=models.UUIDField(default=uuid.uuid4))

    def __str__(self):
        return self.name
    
##### models product ########
class Product(SafeDeleteModel,LifecycleModel):
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.FloatField(max_length=5)
    
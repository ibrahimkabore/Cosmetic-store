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

class Contry(SafeDeleteModel,LifecycleModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(max_length=50)
    history = HistoricalRecords(table_name='image_history',
                                history_id_field=models.UUIDField(default=uuid.uuid4))

    def __str__(self):
        return self.name

class City(SafeDeleteModel,LifecycleModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    _safedelete_policy = SOFT_DELETE_CASCADE
    name = models.CharField(max_length=50)
    contry = models.ForeignKey(Contry, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


class Users(AbstractUser,SafeDeleteModel):
    
    _safedelete_policy = SOFT_DELETE_CASCADE
    
    

   

import random
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row,Column
from django.core.mail import send_mail
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import modelformset_factory
from django import forms

from .models import *
from django.forms import  DateTimeInput



#formulaire de connexion
class LoginForm(AuthenticationForm): 
    
    username = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur ou e-mail', 'id': 'username'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'id': 'password'})
    )

#formualaire de verification
class VerificationForm(forms.Form):
 
    code = forms.CharField(max_length=6)
    


#formualire de creation de compte 
class  CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name','last_name', 'email','Contact','username','password1', 'password2')
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet e-mail existe déjà.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Désactiver le compte jusqu'à la vérification
        if commit:
            user.save()
            code = str(random.randint(100000, 999999))
            VerificationCode.objects.create(user=user, code=code)
            send_mail(
                'Votre code de vérification',
                f'Votre code de vérification est {code}',
                'kaboremessi@gmail.com',
                [user.email],
                fail_silently=False,
            )
        return user
 
# 2ath

class TwoFactorMethodForm(forms.Form):
    two_factor_method = forms.ChoiceField(
        choices=[
            ('email', 'Receive Code by Email'),
            ('google_auth', 'Use Google Authenticator')
        ],
        widget=forms.RadioSelect,
        label="Choose Two-Factor Authentication Method"
    )

class EmailVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 6-digit code'})
    )

class GoogleAuthVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Google Authenticator code'})
    )
    
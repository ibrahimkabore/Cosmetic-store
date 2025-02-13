from django.shortcuts import render, redirect
from django.contrib.auth import login,logout,get_backends
from e_commerce.forms import *
from django.shortcuts import redirect
from e_commerce.models import VerificationCode
from django.contrib.auth.decorators import login_required
# view de creation de compte 
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views
 

import random
from django.core.mail import send_mail
import pyotp
import qrcode
import io
import base64

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None        
    
       
def register(request):
    
    GENDER_CHOICES = [
        ('H', _('Homme')),
        ('F', _('Femme')),
        ('A', _('Autre'))
    ]
    if request.method == 'POST':
        form = CustomUserForm(request.POST , request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('verify')  # Rediriger vers la page de vérification
    else:
        form = CustomUserForm()
    return render(request, 'registration/register.html', {'form': form, 'GENDER_CHOICES': GENDER_CHOICES})

# view de verification de creation de compte 

def verify(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                verification_code = VerificationCode.objects.get(code=code)
                user = verification_code.user
                user.is_active = True
                user.is_verified = True
                user.save()
                verification_code.delete()  # Supprimer le code de vérification après validation
                
                # Obtenir le backend d'authentification utilisé
                backend = get_backends()[0]
                login(request, user, backend='accounts.auth_backends.EmailOrUsernameModelBackend')
                return redirect('login')
            except VerificationCode.DoesNotExist:
                form.add_error('code', 'Code invalide')
    else:
        form = VerificationForm()
    return render(request, 'registration/verify.html', {'form': form})

"""
# view de connexion """
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Store user in session for two-factor process
            request.session['pre_2fa_user_id'] = user.id
            return redirect('two_factor_method')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def two_factor_method(request):
    if 'pre_2fa_user_id' not in request.session:
        return redirect('login')
    
    user = CustomUser.objects.get(id=request.session['pre_2fa_user_id'])
    
    if request.method == 'POST':
        form = TwoFactorMethodForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['two_factor_method']
            user.two_factor_method = method
            user.save()
            
            if method == 'email':
                # Generate and send email code
                code = str(random.randint(100000, 999999))
                request.session['2fa_email_code'] = code
                send_mail(
                    'Two-Factor Authentication Code',
                    f'Your verification code is: {code}',
                    'your_email@example.com',
                    [user.email],
                    fail_silently=False,
                )
                return redirect('email_verification')
            
            elif method == 'google_auth':
                # Generate Google Authenticator secret
                secret = user.generate_google_auth_secret()
                
                # Generate QR code
                totp = pyotp.TOTP(secret)
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(totp.provisioning_uri(name=user.username, issuer_name='suivi empotage'))
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                qr_code = base64.b64encode(buffered.getvalue()).decode()
                
                return render(request, 'registration/google_auth_setup.html', {
                    'qr_code': qr_code,
                    'secret': secret
                })
    else:
        form = TwoFactorMethodForm()
    
    return render(request, 'registration/two_factor_method.html', {'form': form})

def email_verification(request):
    if 'pre_2fa_user_id' not in request.session or '2fa_email_code' not in request.session:
        return redirect('login')
    
    user = CustomUser.objects.get(id=request.session['pre_2fa_user_id'])
    
    if request.method == 'POST':
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if code == request.session['2fa_email_code']:
                # Specify the backend explicitly
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                del request.session['2fa_email_code']
                return redirect('index')
            else:
                messages.error(request, 'Invalid verification code')
    else:
        form = EmailVerificationForm()
    
    return render(request, 'registration/email_verification.html', {'form': form})

def google_auth_verification(request):
    if 'pre_2fa_user_id' not in request.session:
        return redirect('login')
    
    user = CustomUser.objects.get(id=request.session['pre_2fa_user_id'])
    
    if request.method == 'POST':
        form = GoogleAuthVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            if user.verify_google_auth_code(code):
                # Specify the backend explicitly
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                return redirect('index')
            else:
                messages.error(request, 'Invalid authentication code')
    else:
        form = GoogleAuthVerificationForm()
    
    return render(request, 'registration/google_auth_verification.html', {'form': form})

@login_required
def deconnection(request):
    logout(request)
    # Redirige l'utilisateur vers une page après la déconnexion (par exemple la page d'accueil)
    messages.add_message(request, messages.SUCCESS, " A bientot  " )

    return redirect('login')

#view reste password


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/rest/password_reset.html'

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            messages.error(self.request, "Cet email n'est associé à aucun compte utilisateur.")
            return self.form_invalid(form)
        return super().form_valid(form)

from django.shortcuts import render


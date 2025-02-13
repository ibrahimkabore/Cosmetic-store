from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@login_required
def favoris (request):
   
    
    return render(request, 'home/favoris.html')
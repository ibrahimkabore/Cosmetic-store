from django.shortcuts import get_object_or_404, render
from e_commerce.models import Product,Favorite
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'favorites.html', {
        'favorites': favorites
    })
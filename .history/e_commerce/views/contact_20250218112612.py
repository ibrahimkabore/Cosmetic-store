
from django.shortcuts import render

from e_commerce.models import CartItem


def contact (request):
    number =CartItem.objects.count
    
    return render(request,'home/contact.html',{'number':number})
from django.http import HttpResponse
from django.shortcuts import render

#### error 404 #######
def Home(request):
    
    
    return render(request, 'home/')


### error 500   ####### 
from django.http import HttpResponse
from django.shortcuts import render

#### error 404 #######
def Home(request, exception):
    return render(request, 'home/404.', {}, status=404)


### error 500   ####### 
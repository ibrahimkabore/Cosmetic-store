from django.http import HttpResponse
from django.shortcuts import render

#### error 404 #######
def page_not_found_view(request, exception):
    return render(request, '404.html', {}, status=404)


### error 500   #######


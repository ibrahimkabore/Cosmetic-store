from django.http import HttpResponse
from django.shortcuts import render

def page_not_found_view(request, exception):
    return render(request, '404.html', {}, status=404)


def votre_vue(request):
    return HttpResponse("Page personnalisée accessible")
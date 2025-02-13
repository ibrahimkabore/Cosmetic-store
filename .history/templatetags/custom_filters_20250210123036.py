import os
from django import template

from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        # Convertir en string et inverser
        str_value = str(int(value))[::-1]
        # Ajouter les points tous les 3 chiffres
        groups = [str_value[i:i+3] for i in range(0, len(str_value), 3)]
        # Rejoindre avec des points et réinverser
        formatted = '.'.join(groups)[::-1]
        return formatted
    except (ValueError, TypeError):
        return value
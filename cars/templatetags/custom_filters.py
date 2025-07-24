# mycarreseller/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Permite acessar um item de um dicionário usando uma chave no template.
    Ex: {{ my_dict|get_item:key }}
    """
    return dictionary.get(key)

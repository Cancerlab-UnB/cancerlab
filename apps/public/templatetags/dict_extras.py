# apps/public/templatetags/dict_extras.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acessar dict[key] em templates: {{ mydict|get_item:key }}"""
    if dictionary is None:
        return ""
    try:
        val = dictionary.get(key, "")
    except AttributeError:
        return ""
    if val is None:
        return ""
    # Formata floats sem casa decimal desnecessária
    try:
        import math
        if isinstance(val, float) and math.isnan(val):
            return ""
    except Exception:
        pass
    return val

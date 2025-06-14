from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def getlist(querydict, key):
    return querydict.getlist(key)

@register.simple_tag
def querystring(request, **kwargs):
    updated = request.GET.copy()
    for k, v in kwargs.items():
        if v == '':
            updated.pop(k, None)
        else:
            updated[k] = v
    return updated.urlencode()


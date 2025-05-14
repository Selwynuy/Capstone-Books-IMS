from django import template

register = template.Library()

@register.filter
def split_keywords(value):
    if not value:
        return []
    return [kw.strip() for kw in value.split(',') if kw.strip()] 
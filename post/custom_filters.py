from django import template

register = template.Library()

@register.filter
def pluck(queryset, attr):
    return [getattr(obj, attr) for obj in queryset]

@register.filter
def contains(value, arg):
    return arg in value

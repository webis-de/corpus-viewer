from django import template

register = template.Library()

@register.filter
def get(item, field):
    try:
        return item[field]
    except TypeError:
        return getattr(item, field)

@register.filter
def get_display_name(field, settings):
    return settings['data_fields'][field]['display_name']

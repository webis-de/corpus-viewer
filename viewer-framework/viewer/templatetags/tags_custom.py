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

@register.filter
def display_as_tag_classes(list_tags):
    result = ''

    try:
        for tag in list_tags:
            result += 'tag_' + str(tag.id) + ' '
    except TypeError:
        for tag in list_tags.all():
            result += 'tag_' + str(tag.id) + ' '

    return result.strip()

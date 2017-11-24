from django import template
from viewer.views.shared_code import glob_manager_data 

register = template.Library()

@register.simple_tag(takes_context=True)
def get_state_sorted(context, field):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    list_sorted_columns = context.request.session[current_corpus]['viewer__viewer__sorted_columns']

    for obj_sorted_column in list_sorted_columns:
        if obj_sorted_column['field'] == field:
            return obj_sorted_column['order']

    return 'None'

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_filters(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_filters']

@register.simple_tag(takes_context=True)
def get_has_template_view_item(context):
    id_corpus = context.request.session['viewer__viewer__current_corpus']
    return glob_manager_data.get_setting_for_corpus('template_html', id_corpus) != None

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_tags(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_tags']

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_settings(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_settings']
 
@register.simple_tag(takes_context=True)
def get_is_allowed_editing(context):
    id_corpus = context.request.session['viewer__viewer__current_corpus']
    return glob_manager_data.is_editing_allowed(id_corpus)
 
@register.simple_tag(takes_context=True)
def get_values_filter(context, filter_custom):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__viewer__filter_custom'][filter_custom['data_field']]

@register.simple_tag(takes_context=True)
def get_tags(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__viewer__filter_tags']

@register.filter
def in_columns_checked(key, request):
    current_corpus = request.session['viewer__viewer__current_corpus']
    return key in request.session[current_corpus]['viewer__viewer__columns']

@register.filter
def get_is_filter_for_alphanumeric(key, settings):
    # current_corpus = request.session['viewer__viewer__current_corpus']
    # return key in request.session[current_corpus]['viewer__viewer__columns']
    return settings['data_fields'][key]['type'] == 'string' or settings['data_fields'][key]['type'] == 'text'

@register.filter
def get(item, field):
    try:
        return item[field]
    except TypeError:
        return getattr(item, field)

@register.filter
def get_type_field(field, settings):
    return settings['data_fields'][field]['type'].lower()

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

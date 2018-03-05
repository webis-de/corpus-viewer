from django import template
from viewer.views.shared_code import glob_manager_data 
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def get_urls_header(context):
    try:
        id_corpus = context.request.session['viewer__viewer__current_corpus']
    except KeyError:
        return []
        
    return glob_manager_data.get_setting_for_corpus('urls_header', id_corpus)

@register.simple_tag(takes_context=True)
def get_state_sorted(context, field):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    list_sorted_columns = context.request.session[current_corpus]['viewer__viewer__sorted_columns']

    for obj_sorted_column in list_sorted_columns:
        if obj_sorted_column['field'] == field:
            return obj_sorted_column['order']

    return 'None'



@register.simple_tag(takes_context=True)
def get_width_filters(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__width_filters']

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_filters(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_filters']

@register.simple_tag(takes_context=True)
def get_has_template_view_item(context):
    id_corpus = context.request.session['viewer__viewer__current_corpus']
    return glob_manager_data.get_setting_for_corpus('template_html', id_corpus) != None or glob_manager_data.get_setting_for_corpus('external_source', id_corpus) != None

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_tags(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_tags']

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_selections(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_selections']

@register.simple_tag(takes_context=True)
def get_is_collapsed_div_settings(context):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    return context.request.session[current_corpus]['viewer__is_collapsed_div_settings']
 
@register.simple_tag(takes_context=True)
def get_is_allowed_editing(context):
    id_corpus = context.request.session['viewer__viewer__current_corpus']
    return glob_manager_data.get_has_access_to_editing(id_corpus, context.request)

@register.simple_tag(takes_context=True)
def get_has_secret_token_editing(context):
    id_corpus = context.request.session['viewer__viewer__current_corpus']
    return glob_manager_data.has_corpus_secret_token_editing(id_corpus)
 
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

@register.simple_tag(takes_context=True)
def get_count_items(context, tag):
    current_corpus = context.request.session['viewer__viewer__current_corpus']
    related_name = glob_manager_data.get_setting_for_corpus('database_related_name', current_corpus)
    return getattr(tag, related_name).count()

@register.filter
def get(item, field):
    try:
        return item[field]
    except TypeError:
        try:
            value = item
            for attribute in field.split('__'):
                value = getattr(value, attribute)
            return value
        except AttributeError:
            return item.id

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


@register.simple_tag(takes_context=True)
def get_dark_mode(context):
    try:
        return context.request.session['viewer__dark_mode']
    except KeyError:
        context.request.session['viewer__dark_mode'] = False
        return False

@register.simple_tag(takes_context=True)
def get_html_dark_mode(context):
    html = """
        <label class="switch align-self-center mb-0 ml-3" title="Toggle dark mode">
            <input id="button_toggle_dark_mode" type="checkbox" {checked}>
            <span class="slider round"></span>
        </label>
    """

    is_dark_mode = False
    try:
        is_dark_mode = context.request.session['viewer__dark_mode']
    except KeyError:
        context.request.session['viewer__dark_mode'] = is_dark_mode

    return mark_safe(
        html.format(
            checked = 'checked' if is_dark_mode else ''
        )
    )
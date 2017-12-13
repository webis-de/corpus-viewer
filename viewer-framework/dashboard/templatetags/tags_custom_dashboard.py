from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_html_state_loaded(state):
    string_template = """
        <span class="pull-right align-middle {color}" data-toggle="tooltip" data-placement="top" title="{tooltip}">
            <span class="fa-stack" style="font-size: 0.4em">
                <i class="fa fa-square-o fa-stack-2x"></i>
                <i class="fa {icon} fa-stack-1x" style="top: -1px;"></i>
            </span>
        </span>
    """

    if state == 'loaded':
        return string_template.format(
            color='text-success',
            icon='fa-check',
            tooltip='Indexed'
        )
    elif state == 'not_loaded':
        return string_template.format(
            color='text-danger',
            icon='fa-times',
            tooltip='Not indexed'
        )
    elif state == 'loading':
        return string_template.format(
            color='text-warning',
            icon='fa-refresh fa-spin',
            tooltip='Currently Indexing'
        )

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
        <div class="col d-flex justify-content-end">
            <label class="switch align-self-center mb-0" title="Toggle dark mode">
                <input id="button_toggle_dark_mode" type="checkbox" {checked}>
                <span class="slider round"></span>
            </label>
        </div>
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
    
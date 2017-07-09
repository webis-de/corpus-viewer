from django import template

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
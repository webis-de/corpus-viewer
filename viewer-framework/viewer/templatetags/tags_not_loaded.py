from django import template
from viewer.classes.data.Manager_Data import Manager_Data 

register = template.Library()
from django.utils.safestring import mark_safe


@register.simple_tag(takes_context=True)
def check_is_loading(context):
    return context['state_loaded'] == Manager_Data.State_Loaded.LOADING

@register.filter
def prepare_for_html(value):
	value = value.replace('<', '&lt;').replace('>', '&gt;')
	value = mark_safe("&nbsp;".join(value.split(' ')))
	return value
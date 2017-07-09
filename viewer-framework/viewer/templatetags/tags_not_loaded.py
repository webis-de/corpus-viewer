from django import template
from viewer.classes.data.Manager_Data import * 

register = template.Library()

@register.simple_tag(takes_context=True)
def is_loading(context):

    return context['state_loaded'] == Manager_Data.State_Loaded.LOADING

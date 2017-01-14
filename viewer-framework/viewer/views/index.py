from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render
from django.apps import apps


def index(request):
    # request.session.flush()
##### handle session entries
    for viewer__filter in  DICT_SETTINGS_VIEWER['filters']:
        if viewer__filter['type'] == 'text':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_id'], viewer__filter['default_value'])
        elif viewer__filter['type'] == 'checkbox':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_id'], True if viewer__filter['default_value'] == 'checked' else False)

    set_session(request, 'is_collapsed_div_filters', True)

    # print(request.session['viewer__filter_text_content'])
##### apply filters
    # if DICT_SETTINGS_VIEWER['data_type'] == 'database':
    #     print(DICT_SETTINGS_VIEWER['model_name'])
    print(apps.get_model("adsadsad"))
##### handle post requests
    # print(DICT_SETTINGS_VIEWER)
    context = {}
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)

def tags(request):
    context = {}
    return render(request, 'viewer/tags.html', context)

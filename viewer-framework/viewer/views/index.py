from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_session_entry':
            request.session['viewer__'+obj['session_key']] = obj['session_value']
            response['status'] = 'success'
        return JsonResponse(response)
    # index_example_data()
    # request.session.flush()
    set_session(request, 'is_collapsed_div_filters', True)
    set_session(request, 'is_collapsed_div_tags', True)
    set_session_from_url(request, 'viewer__columns', DICT_SETTINGS_VIEWER['displayed_fields'], is_array=True)

    dict_url_params = get_url_params(request)
    context = {}
    context['json_url_params'] = json.dumps(dict_url_params)
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)

def get_url_params(request):
    dict_url_params = request.GET.copy()

    if 'viewer__columns' in dict_url_params:
        dict_url_params['viewer__columns'] = json.loads(dict_url_params['viewer__columns'])
    else:
        dict_url_params['viewer__columns'] = request.session['viewer__viewer__columns']

    return dict_url_params

def tags(request):
    context = {}
    return render(request, 'viewer/tags.html', context)
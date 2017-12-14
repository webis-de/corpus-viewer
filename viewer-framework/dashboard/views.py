from django.shortcuts import render
import os
import importlib
import glob
import json
import collections
from django.core.cache import cache
from django.http import JsonResponse
from viewer.views.shared_code import glob_manager_data

def index(request):
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_current_corpus':
        	request.session['viewer__current_corpus'] = obj['corpus']
        elif obj['task'] == 'get_corpora':
            response['data'] = get_corpora()
        elif obj['task'] == 'refresh_corpora':
            response['data'] = refresh_corpora()
        elif obj['task'] == 'set_session_entry':
            request.session['viewer__'+obj['session_key']] = obj['session_value']
            response['status'] = 'success'
        return JsonResponse(response)

    context = {}
    context['mode_navbar'] = 'dashboard'
    # context['id_corpus'] = id_corpus
    return render(request, 'dashboard/index.html', context)

def documentation(request):
    context = {}

    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_session_entry':
            request.session['viewer__'+obj['session_key']] = obj['session_value']
            response['status'] = 'success'
        return JsonResponse(response)

    with open(os.path.join('..', 'settings', 'settings_viewer_example.py')) as f:
        context['example_setting_file'] = f.read()

    context['url_host'] = 'http://webis24.medien.uni-weimar.de:8080'
    context['name_host'] = 'webis24'
    context['mode_navbar'] = 'documentation'
    return render(request, 'dashboard/documentation.html', context)

def delete_session(request):
    request.session.flush()
    return JsonResponse({})
    
def refresh_corpora():
    glob_manager_data.check_for_new_corpora()
    return get_corpora()

def get_corpora():
    response = {}

    # dict_data_chached = init_data()
    dict_ordered = collections.OrderedDict()
    list_keys = ['name', 'description']
    print('#################################')
    for id_corpus in glob_manager_data.get_ids_corpora(sorted_by='name'):
        settings_total = glob_manager_data.get_settings_for_corpus(id_corpus)
        settings = {key: settings_total[key] for key in list_keys}
        settings['state_loaded'] = glob_manager_data.get_state_loaded(id_corpus)
        settings['has_secret_token'] = glob_manager_data.has_corpus_secret_token(id_corpus)
        dict_ordered[id_corpus] = settings

    response['corpora'] = dict_ordered

    response['corpora_with_exceptions'] = glob_manager_data.get_corpora_with_exceptions()

    return response

# def init_data():
#     dict_data = cache.get('metadata_corpora')

#     if(dict_data == None):
#         dict_data = {}

#     return dict_data
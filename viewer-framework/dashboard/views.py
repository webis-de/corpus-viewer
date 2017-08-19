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
        return JsonResponse(response)

    context = {}
    # print(context['corpora'].items())
    return render(request, 'dashboard/index.html', context)

def refresh_corpora():
    # print(glob_manager_data.dict_corpora)
    glob_manager_data.check_for_new_corpora()
    # print(glob_manager_data.dict_corpora)
    return get_corpora()

def get_corpora():
    response = {}

    dict_data_chached = init_data()
    dict_ordered = collections.OrderedDict()
    list_keys = ['name', 'description']
    for id_corpus in glob_manager_data.get_ids_corpora(sorted_by='name'):
        settings_total = glob_manager_data.get_settings_for_corpus(id_corpus)
        settings = {key: settings_total[key] for key in list_keys}
        settings['state_loaded'] = glob_manager_data.get_state_loaded(id_corpus)
        dict_ordered[id_corpus] = settings

    # print(dict_ordered)
    response['corpora'] = dict_ordered

    return response

def init_data():
    dict_data = cache.get('metadata_corpora')

    if(dict_data == None):
        dict_data = {}

    return dict_data
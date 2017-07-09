from django.shortcuts import render
import os
import importlib
import glob
import json
import collections
from django.core.cache import cache
from viewer.views.shared_code import glob_settings

# glob_settings = {}
# glob_current_key = 'settings_viewer_arg'

# modules = glob.glob('settings_viewer/*.py')
# __all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
# for corpus in __all__:
#     module_settings = importlib.import_module('settings_viewer.'+corpus)
#     glob_settings[corpus] = module_settings.DICT_SETTINGS_VIEWER

def index(request):
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_current_corpus':
        	request.session['viewer__current_corpus'] = obj['corpus']

    context = {}

    dict_data_chached = init_data()

    dict_ordered = collections.OrderedDict()
    for key in sorted(glob_settings.keys(), key=lambda corpus: glob_settings[corpus]['name']):
        state_loaded = 'not_loaded'

        if key in dict_data_chached:
            if dict_data_chached[key]['is_loaded'] == True:
                state_loaded = 'loaded'
            else:
                state_loaded = 'loading'

        glob_settings[key]['viewer__state_loaded'] = state_loaded
        dict_ordered[key] = glob_settings[key]



    context['corpora'] = dict_ordered
    # print(context['corpora'].items())
    return render(request, 'dashboard/index.html', context)

def init_data():
    dict_data = cache.get('metadata_corpora')

    if(dict_data == None):
        dict_data = {}

    return dict_data
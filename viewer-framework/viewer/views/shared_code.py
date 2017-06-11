import json
import csv
import os
import importlib
import time
import glob
from django.core.cache import cache
from viewer.models import m_Tag, m_Entity

modules = glob.glob('settings_viewer/*.py')
__all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
glob_settings = {}
for corpus in __all__:
    module_settings = importlib.import_module('settings_viewer.'+corpus)
    glob_settings[corpus] = module_settings.DICT_SETTINGS_VIEWER

glob_cache = {}
# cache.set('data_', {})

def get_or_create_tag(name, request, defaults={}):
    name = name.strip()
    name = name.replace(' ', '-')
    db_obj_tag = m_Tag.objects.get_or_create(name=name, key_corpus=get_current_corpus(request), defaults=defaults)

    return db_obj_tag

def load_data(request):
    data = []
    data_only_ids = []
    dict_ids = {}

    key_cache = 'data_' + get_current_corpus(request)
    start = time.perf_counter()
    try:
        data_cached = glob_cache[key_cache]
    except KeyError:
        data_cached = None
    # data_cached = cache.get(key_cache)
    print('time for loading data from cache: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
    use_cache = False
    if data_cached != None:
        if len(data_cached) != 0 and get_setting('use_cache', request=request):
            use_cache = True
        
    if use_cache:
        print('using cache')
        data, data_only_ids, dict_ids = data_cached

        return data, data_only_ids, dict_ids
    else:
        print('not using cache')
        if get_setting('data_type', request=request) == 'database':
            data = model_custom.objects.all()
            data_only_ids = [str(getattr(entity, get_setting('id', request=request))) for entity in model_custom.objects.all().only(get_setting('id', request=request))]

            return data, data_only_ids, dict_ids
        else:
            if get_setting('data_type', request=request) == 'csv-file':
                data = load_file_csv(request)
            elif get_setting('data_type', request=request) == 'ldjson-file':
                data = load_file_ldjson(request)
            elif get_setting('data_type', request=request) == 'custom':
                data = get_setting('load_data_function', request=request)()
            # list of ids
            data_only_ids = [str(item[get_setting('id', request=request)]) for item in data]
            # dictionary id:index in list
            dict_ids = {str(item[get_setting('id', request=request)]):index for index, item in enumerate(data)}
        
        if get_setting('use_cache', request=request):
            glob_cache[key_cache] = (data, data_only_ids, dict_ids)
            # cache.set(key_cache, (data, data_only_ids, dict_ids))

        return data, data_only_ids, dict_ids

def load_file_csv(request):
    data = []
    with open(get_setting('data_path', request=request), newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            tmp = {}
            for index, field in enumerate(get_setting('data_structure', request=request)):
                tmp[field] = row[index]
            data.append(tmp)
    return data

def load_file_ldjson(request):
    # with open(get_setting('data_path'), 'w') as file:
    #     for i in range(100000):
    #         obj = {
    #             'id': str(i),
    #             'name': 'ldjson_'+str(i),
    #             'count_of_something': i*i
    #         }
    #         file.write(json.dumps(obj)+'\n')


    data = []
    with open(get_setting('data_path', request=request), 'r') as file:
        for row in file:
            obj = json.loads(row)
            tmp = {}
            for field in get_setting('data_structure', request=request):
                tmp[field] = obj[field]
            data.append(tmp)
    return data

# def index_example_data():
#     model_custom.objects.all().delete()
#     m_Entity.objects.all().delete()
#     m_Tag.objects.all().delete()
#     list_entries = []
#     for i in range(2000):
#         list_entries.append(model_custom(name='name'+str(i), count_of_something=i))

#     model_custom.objects.bulk_create(list_entries)

def set_sessions(request):
    set_session_from_url(request, 'viewer__current_corpus', default=list(glob_settings.keys())[0])
        
    set_session(request, 'is_collapsed_div_filters', default=True)
    set_session(request, 'is_collapsed_div_tags', default=True)
    set_session(request, 'is_collapsed_div_settings', default=True)
    set_session(request, 'viewer__selected_tags', default=[])

    set_session_from_url(request, 'viewer__page', default=1)

    set_session_from_url(request, 'viewer__columns', default=get_setting('displayed_fields', request=request) + ['viewer__item_selection', 'viewer__tags'], is_json=True)
    set_session_from_url(request, 'viewer__filter_tags', default=[], is_json=True)

    set_session_from_url(request, 'viewer__filter_custom', default={obj_filter['data_field']:obj_filter['default_value'] for obj_filter in get_setting('filters', request=request)}, is_json=True)
    
    # in case of newly added filters add them
    dict_tmp = {obj_filter['data_field']:obj_filter['default_value'] for obj_filter in get_setting('filters', request=request)}
    dict_tmp.update(request.session['viewer__viewer__filter_custom'])
    request.session['viewer__viewer__filter_custom'] = dict_tmp.copy()

def set_session(request, key, default):
    sessionkey = 'viewer__'+key

    if sessionkey not in request.session:
        request.session[sessionkey] = default

def set_session_from_url(request, key, default, is_json=False):
    sessionkey = 'viewer__'+key

    if request.GET.get(key) != None:
        if is_json:
            request.session[sessionkey] = json.loads(request.GET.get(key))
        else:
            request.session[sessionkey] = request.GET.get(key)
    else:
        if sessionkey not in request.session:
            request.session[sessionkey] = default
            
def get_current_corpus(request):
    return request.session['viewer__viewer__current_corpus']

def get_setting(key = None, request = None):
    if key == None:
        return glob_settings[get_current_corpus(request)]

    if key in glob_settings[get_current_corpus(request)]:
        return glob_settings[get_current_corpus(request)][key]

    if key == 'use_cache':
        return False;
    elif key == 'page_size':
        return 25;

    raise ValueError('setting-key \''+key+'\' not found')

# module_custom = importlib.import_module(get_setting('app_label')+'.models')
# model_custom = getattr(module_custom, get_setting('model_name'))

import json
import csv
import os
import time
import sys
import pickle as marshal
# import marshal
# import struct 
# import msgpack
# from struct import *
from django.core.cache import cache
from viewer.models import m_Tag, m_Entity
from viewer.classes.data.Manager_Data import Manager_Data

# modules = glob.glob('settings_viewer/*.py')
# __all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
# print(DICT_SETTINGS_VIEWER)
# glob_settings = {}
# print('############')
# with open('/home/yiro4618/Documents/hiwi/wstud-viewer-framework-django/viewer-framework/settings_viewer/settings_viewer_large_corpus.py', 'r') as f:
#     # print(compile(f.read(), '<string>', 'exec'))
#     exec(compile(f.read(), '<string>', 'exec'))
#     print(DICT_SETTINGS_VIEWER)
# print('############')

# print(DICT_SETTINGS_VIEWER['load_data_function'](3))

# with open('/home/yiro4618/Documents/hiwi/wstud-viewer-framework-django/viewer-framework/settings_viewer/settings_viewer_test.py', 'r') as f:
#     exec(compile(f.read(), '<string>', 'exec'))
# print(DICT_SETTINGS_VIEWER['load_data_function'](3))
# for corpus in __all__:
#     module_settings = importlib.import_module('settings_viewer.'+corpus)
#     glob_settings[corpus] = module_settings.DICT_SETTINGS_VIEWER

glob_manager_data = Manager_Data()
# cache.set('data_', {})


def get_filters_if_not_empty(request, id_corpus):
    dict_filters = request.session[id_corpus]['viewer__viewer__filter_custom'].copy()
    dict_filters['viewer__filter_tags'] = request.session[id_corpus]['viewer__viewer__filter_tags'].copy()

    is_empty = True
    for values in dict_filters.values():
        if len(values) != 0:
            is_empty = False
            break

    if is_empty == True:
        return None 
    else:
        return dict_filters

def get_or_create_tag(name, request, defaults={}):
    name = name.strip()
    name = name.replace(' ', '-')
    db_obj_tag = m_Tag.objects.get_or_create(name=name, key_corpus=get_current_corpus(request), defaults=defaults)

    return db_obj_tag

def load_data(request):
    current_corpus = get_current_corpus(request)
    data = write_corpus(request)
    data = load_corpus(request)
    
    return glob_cache[current_corpus]['list']


    data = []
    data_only_ids = []
    dict_ids = {}

    # key_cache = 'data_' + get_current_corpus(request)
    # start = time.perf_counter()
    # try:
    #     data_cached = glob_cache[key_cache]
    # except KeyError:
    #     data_cached = None
    # data_cached = cache.get(key_cache)
    # print('time for loading data from cache: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
    # use_cache = False
    # if data_cached != None:
    #     if len(data_cached) != 0 and get_setting('use_cache', request=request):
    #         use_cache = True
        
# if use_cache:
#     print('using cache')
#     data, data_only_ids, dict_ids = data_cached

#     return data, data_only_ids, dict_ids
# else: 
    # print('not using cache')
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
            # data = write_corpus(request)
            data = load_corpus(request)
            pass
        # list of ids
        data_only_ids = [str(item[get_setting('id', request=request)]) for item in data]
        # dictionary id:index in list
        dict_ids = {str(item[get_setting('id', request=request)]):index for index, item in enumerate(data)}
    
    # if get_setting('use_cache', request=request):
    #     glob_cache[key_cache] = (data, data_only_ids, dict_ids)
    #     cache.set(key_cache, (data, data_only_ids, dict_ids))
    # write_to_file(data, request)

    return data, data_only_ids, dict_ids

def get_items_by_indices(list_indices, metadata):
    list_result = []

    list_items = glob_cache[metadata[0]]['list']
    index_items = glob_cache[metadata[0]]['index']
    file = metadata[1]

    for index in list_indices:
        item = index_items[list_items[index]]

        file.seek(item['offset_in_bytes'])

        list_result.append(marshal.loads(file.read(item['size_in_bytes'])))

    return list_result

def get_item_by_ids(list_ids, metadata):
    list_result = []

    index_items = glob_cache[metadata[0]]['index']
    file = metadata[1]

    for id_item in list_ids:
        item = index_items[id_item]

        file.seek(item['offset_in_bytes'])
        # file.seek(item[1])

        list_result.append(marshal.loads(file.read(item['size_in_bytes'])))
        # list_result.append(marshal.loads(file.read(item[2])))

    return list_result

def get_item_by_index(index, metadata):
    id_item = glob_cache[metadata[0]]['list'][index]

    item = glob_cache[metadata[0]]['index'][id_item]

    offset_in_bytes = item['offset_in_bytes']
    size_in_bytes = item['size_in_bytes']

    metadata[1].seek(offset_in_bytes)
    item_bin = metadata[1].read(size_in_bytes)

    marshal.loads(item_bin)

def get_item_by_id(id_item, metadata):
    offset_in_bytes = glob_cache[metadata[0]]['index'][id_item]['offset_in_bytes']
    size_in_bytes = glob_cache[metadata[0]]['index'][id_item]['size_in_bytes']

    metadata[1].seek(offset_in_bytes)
    item_bin = metadata[1].read(size_in_bytes)

    return marshal.loads(item_bin)

def load_corpus(request):
    start = time.perf_counter()
    field_id = get_setting_for_corpus(get_current_corpus(request), key='id')
    
    current_corpus = get_current_corpus(request)

    id_item = glob_cache[current_corpus]['list'][10]

    with open(os.path.join(glob_path_cache, current_corpus + '.marshal'), 'rb') as f:
        data = (current_corpus, f, field_id)

        start = time.perf_counter()
        for index in range(0, glob_cache[current_corpus]['size']):
            pass
        print('iterating over whole corpus: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

        # start = time.perf_counter()
        # for index in range(0, glob_cache[current_corpus]['size']):
        #     get_item_by_index(index, metadata=data)
        # print('iterating over whole corpus: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

        start = time.perf_counter()
        get_items_by_indices(range(0, glob_cache[current_corpus]['size']), data)
        print('iterating over whole corpus: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')


        # print(get_item_by_id(id_item=id_item, metadata=data))

    print('loading time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

    return []

def write_corpus(request):
    start = time.perf_counter()
    
    field_id = get_setting_for_corpus(get_current_corpus(request), key='id')

    current_corpus = get_current_corpus(request)
    glob_cache[current_corpus] = {}
    glob_cache[current_corpus]['is_loaded'] = False
    glob_cache[current_corpus]['size'] = 0
    glob_cache[current_corpus]['size_in_bytes'] = 0
    glob_cache[current_corpus]['index'] = {}
    glob_cache[current_corpus]['list'] = []
    
    with open(os.path.join(glob_path_cache, current_corpus + '.marshal'), 'wb') as f:
        data = (current_corpus, f, field_id)
        get_setting('load_data_function', request=request)(data, add_item)

    cache.set('metadata_corpora', glob_cache)

    print('size of corpus: '+str(glob_cache[current_corpus]['size']))
    print('size of corpus (bytes): '+str(glob_cache[current_corpus]['size_in_bytes']))
    print('writing time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
    print('')

    return []

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

def set_sessions(request, id_corpus):
    glob_manager_data.set_current_corpus(request, id_corpus)

    # check if the corpus is still loaded
    if not glob_manager_data.check_if_corpus_available(id_corpus):
        return False

    set_session(request, 'width_filters', default=True)
    set_session(request, 'is_collapsed_div_filters', default=True)
    set_session(request, 'is_collapsed_div_selections', default=True)
    set_session(request, 'is_collapsed_div_tags', default=True)
    set_session(request, 'viewer__selected_tags', default=[])

    set_session_from_url(request, 'viewer__page', default=1)

    set_session_from_url(request, 'viewer__columns', default=glob_manager_data.get_setting_for_corpus('displayed_fields', id_corpus) + ['viewer__item_selection', 'viewer__tags', 'viewer__view_item'], is_json=True)
    set_session_from_url(request, 'viewer__sorted_columns', default=[], is_json=True)
    set_session_from_url(request, 'viewer__filter_tags', default=[], is_json=True)
    set_session_from_url(request, 'viewer__filter_custom', default={obj_filter['data_field']:[] for obj_filter in glob_manager_data.get_setting_for_corpus('filters', id_corpus)}, is_json=True)
    # set_session_from_url(request, 'viewer__filter_custom', default={obj_filter['data_field']:obj_filter['default_value'] for obj_filter in glob_manager_data.get_setting_for_corpus(id_corpus) get_setting('filters', request=request)}, is_json=True)

    # in case of newly added filters add them
    dict_tmp = {obj_filter['data_field']:[] for obj_filter in glob_manager_data.get_setting_for_corpus('filters', id_corpus)}
    dict_tmp.update(request.session[get_current_corpus(request)]['viewer__viewer__filter_custom'])
    request.session[get_current_corpus(request)]['viewer__viewer__filter_custom'] = dict_tmp.copy()

    return True

def set_session(request, key, default):
    sessionkey = 'viewer__'+key

    current_corpus = get_current_corpus(request)

    if not current_corpus in request.session:
        request.session[current_corpus] = {}

    if sessionkey not in request.session[current_corpus]:
        request.session[current_corpus][sessionkey] = default

def set_session_from_url(request, key, default, is_json=False):
    sessionkey = 'viewer__'+key

    current_corpus = get_current_corpus(request)
    
    if not current_corpus in request.session:
        request.session[current_corpus] = {}

    if request.GET.get(key) != None:
        if is_json:
            request.session[current_corpus][sessionkey] = json.loads(request.GET.get(key))
        else:
            request.session[current_corpus][sessionkey] = request.GET.get(key)
    else:
        if sessionkey not in request.session[current_corpus]:
            request.session[current_corpus][sessionkey] = default
            
# def set_current_corpus(request):
#     default = list(glob_settings.keys())[0]
#     key = 'viewer__current_corpus'
#     sessionkey = 'viewer__' + key

#     if request.GET.get(key) != None:
#         request.session[sessionkey] = request.GET.get(key)
#     else:
#         if sessionkey not in request.session:
#             request.session[sessionkey] = default

def get_current_corpus(request):
    return request.session['viewer__viewer__current_corpus']

# def get_setting_for_corpus(id_corpus, key = None):
#     return glob_settings[id_corpus][key]

# def get_setting(key = None, request = None):
#     if key == None:
#         return glob_settings[get_current_corpus(request)]

#     if key in glob_settings[get_current_corpus(request)]:
#         return glob_settings[get_current_corpus(request)][key]

#     if key == 'use_cache':
#         return False;
#     elif key == 'page_size':
#         return 25;

#     raise ValueError('setting-key \''+key+'\' not found')

# module_custom = importlib.import_module(get_setting('app_label')+'.models')
# model_custom = getattr(module_custom, get_setting('model_name'))

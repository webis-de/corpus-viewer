import json
import csv
import os
import importlib
import time
import glob
import pickle
import struct
import msgpack
import marshal
# from struct import *
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

glob_path_cache = '../cache'

# print('started')
# counter = 0
# start = time.perf_counter()
# with open(os.path.join(glob_path_cache, 'settings_viewer_large_corpus.ldjson'), 'r') as f:
#     for line in f:
#         pass
#         if counter % 100000 == 0:
#             print(counter)
#         counter += 1
# print(str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
# print('finished')
# 35 000 000
# 2 000 000 000
# 35100000
# 35200000


def get_or_create_tag(name, request, defaults={}):
    name = name.strip()
    name = name.replace(' ', '-')
    db_obj_tag = m_Tag.objects.get_or_create(name=name, key_corpus=get_current_corpus(request), defaults=defaults)

    return db_obj_tag

def load_data(request):
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
            data = write_corpus(request)
            print('')
            print('')
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

def get_item_ldjson(index, metadata):
    id_item = glob_cache[metadata[0]]['list'][index]
    index_unecessary = glob_cache[metadata[0]]['index'][id_item]['index']

    for index_line, line in enumerate(metadata[1]):
        if index_line == index_unecessary:
            obj = json.loads(line)
            print(obj['text'][-20:])
            break

def get_item_binary(index, metadata, with_size=False):
    id_item = glob_cache[metadata[0]]['list'][index]
    offset_in_bytes = glob_cache[metadata[0]]['index'][id_item]['offset_in_bytes']
    size_in_bytes = glob_cache[metadata[0]]['index'][id_item]['size_in_bytes']

    metadata[1].seek(offset_in_bytes)
    if with_size:
        item_bin = metadata[1].read(size_in_bytes)
    else:
        item_bin = metadata[1].read()

    if metadata[3] == 'pickle':
        obj = pickle.loads(item_bin)
        print(obj['text'][-20:])
    elif metadata[3] == 'marshal':
        obj = marshal.loads(item_bin)
        print(obj['text'][-20:])
    elif metadata[3] == 'msgpack':
        obj = msgpack.unpackb(item_bin, encoding='utf-8')
        print(obj['text'][-20:])
    # for index_line, line in enumerate(metadata[1]):
    #     if index_line == index_unecessary:
    #         obj = json.loads(line)
    #         print(obj)
    #         break
    # offset_in_bytes = glob_cache[metadata[0]]['index'][id_item]['offset_in_bytes']
    # metadata[1].seek

def load_corpus(request):
    field_id = get_setting_for_corpus(get_current_corpus(request), key='id')
    
    list_modes = ['ldjson', 'pickle', 'msgpack', 'marshal']
    for mode in list_modes:
        print('LOADING IN MODE '+mode.upper())
        current_corpus = get_current_corpus(request)+'_'+mode

        index = 900000

        if mode == 'ldjson':
            with open(os.path.join(glob_path_cache, current_corpus + '.ldjson'), 'r') as f:
                data = (current_corpus, f, field_id)
                start = time.perf_counter()
                get_item_ldjson(index=index, metadata=data)
                print('loading time ('+mode+'): '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
        elif mode == 'pickle':
            with open(os.path.join(glob_path_cache, current_corpus + '.pickle'), 'rb') as f:
                start = time.perf_counter()
                data = (current_corpus, f, field_id, mode)
                start = time.perf_counter()
                get_item_binary(index=index, metadata=data)
                print('loading time ('+mode+'): '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
                start = time.perf_counter()
                get_item_binary(index=index, metadata=data, with_size=True)
                print('loading time ('+mode+'): '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
        elif mode == 'msgpack':
            with open(os.path.join(glob_path_cache, current_corpus + '.msgpack'), 'rb') as f:
                data = (current_corpus, f, field_id, mode)
                start = time.perf_counter()
                get_item_binary(index=index, metadata=data, with_size=True)
                print('loading time ('+mode+'): '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
        elif mode == 'marshal':
            with open(os.path.join(glob_path_cache, current_corpus + '.marshal'), 'rb') as f:
                data = (current_corpus, f, field_id, mode)
                start = time.perf_counter()
                get_item_binary(index=index, metadata=data)
                print('loading time ('+mode+'): '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
                start = time.perf_counter()
                get_item_binary(index=index, metadata=data, with_size=True)
                print('loading time ('+mode+'): '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

        print('')

    return []

def write_corpus(request):
    field_id = get_setting_for_corpus(get_current_corpus(request), key='id')
    
    list_modes = ['ldjson', 'pickle', 'msgpack', 'marshal']
    for mode in list_modes:
        start = time.perf_counter()
        print('WRITING IN MODE '+mode.upper())

        current_corpus = get_current_corpus(request)+'_'+mode
        glob_cache[current_corpus] = {}
        glob_cache[current_corpus]['size'] = 0
        glob_cache[current_corpus]['size_in_bytes'] = 0
        glob_cache[current_corpus]['index'] = {}
        glob_cache[current_corpus]['list'] = []

        if mode == 'ldjson':
            with open(os.path.join(glob_path_cache, current_corpus + '.ldjson'), 'w') as f:
                data = (current_corpus, f, field_id, mode)
                get_setting('load_data_function', request=request)(data, add_item_ldjson)
        elif mode == 'pickle':
            with open(os.path.join(glob_path_cache, current_corpus + '.pickle'), 'wb') as f:
                data = (current_corpus, f, field_id, mode)
                get_setting('load_data_function', request=request)(data, add_item_pickle)
        elif mode == 'msgpack':
            with open(os.path.join(glob_path_cache, current_corpus + '.msgpack'), 'wb') as f:
                data = (current_corpus, f, field_id, mode)
                get_setting('load_data_function', request=request)(data, add_item_msgpack)
        elif mode == 'marshal':
            with open(os.path.join(glob_path_cache, current_corpus + '.marshal'), 'wb') as f:
                data = (current_corpus, f, field_id, mode)
                get_setting('load_data_function', request=request)(data, add_item_marshal)

        print('size of corpus: '+str(glob_cache[current_corpus]['size']))
        print('size of corpus (bytes): '+str(glob_cache[current_corpus]['size_in_bytes']))
        print('writing time ('+mode+'): '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
        print('')

        # break

    return []

def add_item_ldjson(item, metadata):
    metadata[1].write(json.dumps(item) + '\n')

    glob_cache[metadata[0]]['index'][item[metadata[2]]] = {
        'index': glob_cache[metadata[0]]['size'],
    }


    glob_cache[metadata[0]]['list'].append(item[metadata[2]])

    glob_cache[metadata[0]]['size'] += 1

def add_item_pickle(item, metadata):
    item_bin = pickle.dumps(item, pickle.HIGHEST_PROTOCOL)
    metadata[1].write(item_bin)

    size_in_bytes = len(item_bin)

    glob_cache[metadata[0]]['index'][item[metadata[2]]] = {
        'index': glob_cache[metadata[0]]['size'],
        'offset_in_bytes': glob_cache[metadata[0]]['size_in_bytes'],
        'size_in_bytes': size_in_bytes,
    }

    glob_cache[metadata[0]]['list'].append(item[metadata[2]])
    glob_cache[metadata[0]]['size'] += 1
    glob_cache[metadata[0]]['size_in_bytes'] += size_in_bytes

def add_item_marshal(item, metadata):
    item_bin = marshal.dumps(item)
    metadata[1].write(item_bin)

    size_in_bytes = len(item_bin)

    glob_cache[metadata[0]]['index'][item[metadata[2]]] = {
        'index': glob_cache[metadata[0]]['size'],
        'offset_in_bytes': glob_cache[metadata[0]]['size_in_bytes'],
        'size_in_bytes': size_in_bytes,
    }

    glob_cache[metadata[0]]['list'].append(item[metadata[2]])
    glob_cache[metadata[0]]['size'] += 1
    glob_cache[metadata[0]]['size_in_bytes'] += size_in_bytes

def add_item_msgpack(item, metadata):
    item_bin = msgpack.packb(item)
    metadata[1].write(item_bin)

    size_in_bytes = len(item_bin)

    glob_cache[metadata[0]]['index'][item[metadata[2]]] = {
        'index': glob_cache[metadata[0]]['size'],
        'offset_in_bytes': glob_cache[metadata[0]]['size_in_bytes'],
        'size_in_bytes': size_in_bytes,
    }

    glob_cache[metadata[0]]['list'].append(item[metadata[2]])
    glob_cache[metadata[0]]['size'] += 1
    glob_cache[metadata[0]]['size_in_bytes'] += size_in_bytes

def add_item(item, metadata):
    # ldjson: 3964.2ms
    # msgpack: 2281.27ms
    # pickle: 1480.72ms

    item_bin = msgpack.packb(item)
    # item_bin = pickle.dumps(item, pickle.HIGHEST_PROTOCOL)

    metadata[1].write(item_bin)
    # metadata[1].write(json.dumps(item) + '\n')

    # glob_cache[metadata[0]]['index'][item[metadata[2]]] = {
    #     'index': glob_cache[metadata[0]]['size'],
    #     'size_in_bytes': len(item_bin),
    # }

    # glob_cache[metadata[0]]['size'] += 1
    # print(glob_cache)

    # custom_struct = Struct('<l s')
    # print(custom_struct)


    # "I%ds" % (len(s),), len(s)
    # format_string = ''
    # for key, field in sorted(get_setting('data_fields', request=request).items()):
    #     if field['type'] == 'number':
    #         format_string += 'f '
    #     elif field['type'] == 'string' or field['type'] == 'text':
    #         format_string += '{}s '

    # # print(format_string)

    # with open(get_current_corpus(request)+'.bin', 'wb') as f:
    #     for item in data:
    #         # print(format_string.format(len(item['text'].encode('utf-8'))))
    #         result = struct.pack(format_string.format(len(item['text'].encode('utf-8'))), item['id'], item['text'].encode('utf-8'))
    #         # result = custom_struct.pack(item['id'], item['text'].encode('utf-8'))
    #         # print(result)
    #         f.write(result)

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
    set_current_corpus(request)
        
    set_session(request, 'is_collapsed_div_filters', default=True)
    set_session(request, 'is_collapsed_div_tags', default=True)
    set_session(request, 'viewer__selected_tags', default=[])

    set_session_from_url(request, 'viewer__page', default=1)

    set_session_from_url(request, 'viewer__columns', default=get_setting('displayed_fields', request=request) + ['viewer__item_selection', 'viewer__tags'], is_json=True)
    set_session_from_url(request, 'viewer__filter_tags', default=[], is_json=True)

    set_session_from_url(request, 'viewer__filter_custom', default={obj_filter['data_field']:[] for obj_filter in get_setting('filters', request=request)}, is_json=True)
    # set_session_from_url(request, 'viewer__filter_custom', default={obj_filter['data_field']:obj_filter['default_value'] for obj_filter in get_setting('filters', request=request)}, is_json=True)
    
    # in case of newly added filters add them
    dict_tmp = {obj_filter['data_field']:obj_filter['default_value'] for obj_filter in get_setting('filters', request=request)}
    dict_tmp.update(request.session[get_current_corpus(request)]['viewer__viewer__filter_custom'])
    request.session[get_current_corpus(request)]['viewer__viewer__filter_custom'] = dict_tmp.copy()

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
            
def set_current_corpus(request):
    default = list(glob_settings.keys())[0]
    key = 'viewer__current_corpus'
    sessionkey = 'viewer__' + key

    if request.GET.get(key) != None:
        request.session[sessionkey] = request.GET.get(key)
    else:
        if sessionkey not in request.session:
            request.session[sessionkey] = default

def get_current_corpus(request):
    return request.session['viewer__viewer__current_corpus']

def get_setting_for_corpus(id_corpus, key = None):
    return glob_settings[id_corpus][key]

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

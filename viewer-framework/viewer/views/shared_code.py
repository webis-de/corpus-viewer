import time
import json
import csv
import importlib
import os
import re
from collections import OrderedDict
from django.core.cache import cache
from settings_viewer import DICT_SETTINGS_VIEWER
from viewer.models import m_Tag, m_Entity
from django.apps import apps
module_custom = importlib.import_module(DICT_SETTINGS_VIEWER['app_label']+'.models')
model_custom = getattr(module_custom, DICT_SETTINGS_VIEWER['model_name'])

cache.set('data', {})

def get_or_create_tag(name, defaults={}):
    name = name.strip()
    name = name.replace(' ', '-')
    db_obj_tag = m_Tag.objects.get_or_create(name=name, defaults=defaults)

    return db_obj_tag

def load_data():
    data = []
    data_only_ids = []
    dict_ids = {}

    data_cached = cache.get('data')
    use_cache = False
    if data_cached != None:
        if len(data_cached) != 0 and get_setting('use_cache'):
            use_cache = True
        
    if use_cache:
        print('using cache')
        data, data_only_ids, dict_ids = data_cached

        return data, data_only_ids, dict_ids
    else:
        print('not using cache')
        if DICT_SETTINGS_VIEWER['data_type'] == 'database':
            data = model_custom.objects.all()
            data_only_ids = [str(getattr(entity, DICT_SETTINGS_VIEWER['id'])) for entity in model_custom.objects.all().only(DICT_SETTINGS_VIEWER['id'])]

            return data, data_only_ids, dict_ids
        else:
            if DICT_SETTINGS_VIEWER['data_type'] == 'csv-file':
                data = load_file_csv()
            elif DICT_SETTINGS_VIEWER['data_type'] == 'ldjson-file':
                data = load_file_ldjson()
            elif DICT_SETTINGS_VIEWER['data_type'] == 'custom':
                data = DICT_SETTINGS_VIEWER['load_data_function']()
            # list of ids
            data_only_ids = [str(item[DICT_SETTINGS_VIEWER['id']]) for item in data]
            # dictionary id:index in list
            dict_ids = {str(item[DICT_SETTINGS_VIEWER['id']]):index for index, item in enumerate(data)}
        
        if get_setting('use_cache'):
            cache.set('data', (data, data_only_ids, dict_ids))

        return data, data_only_ids, dict_ids

def load_directory():
    data = []
    
    for entry in DICT_SETTINGS_VIEWER['data_structure']:
        entry['path'] = DICT_SETTINGS_VIEWER['data_path'] 
        data = load_entry(entry)

    return data

def load_entry(entry_input):
    data_result = []

    # entry_type = entry_input['type'][0]
    # entry_count_min = entry_input['type'][1]
    # entry_count_max = entry_input['type'][2]
    # entry_name = entry_input['name']
    entry_is_item = entry_input['is_item'] if 'is_item' in entry_input else False
    # entry_path = entry_input['path']

    if entry_is_item:
        data_result += load_item(entry_input)
    else:
        print('data_result')
        data_result += load_no_item(entry_input)
    return data_result

def load_no_item(entry_input):
    data_result = []

    entry_type = entry_input['type'][0]
    entry_name = entry_input['name']

    if entry_type == 'folder':
        for entry in entry_input['content']:
            entry['path'] = os.path.join(entry_input['path'], entry_name)
            data_result += load_entry(entry)

    return data_result

def load_item(entry_input):
    data_result = []
    
    entry_type = entry_input['type'][0]
    entry_count_max = entry_input['type'][2]
    entry_name = entry_input['name']
    entry_path = entry_input['path']

    if entry_type == 'folder':
        for entry in entry_input['content']:
            if entry_count_max == '*':

                for folder in os.listdir(entry_path):
                    tmp_path = os.path.join(entry_input['path'], folder)
                    tmp_dict = {'id': folder, 'count_of_something': 1, 'name': folder}
                    for entry1 in entry_input['content']:
                        if entry1['type'][0] == 'file-json':
                            entry1['path'] = os.path.join(tmp_path, folder+'.json')

                            with open(entry1['path'], 'r') as file:
                                obj_json = json.loads(file.read())
                                for key in entry1['keys']:
                                    tmp_dict[key[1]] = obj_json[key[0]]

                        # print(entry1['path'])
                        # load_entry(entry1)
                    data_result.append(tmp_dict)

    elif entry_type == 'file-json':
        pass
   
    return data_result

def load_file_csv():
    data = []
    with open(DICT_SETTINGS_VIEWER['data_path'], newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            tmp = {}
            for index, field in enumerate(DICT_SETTINGS_VIEWER['data_structure']):
                tmp[field] = row[index]
            data.append(tmp)
    return data

def load_file_ldjson():
    # with open(DICT_SETTINGS_VIEWER['data_path'], 'w') as file:
    #     for i in range(100000):
    #         obj = {
    #             'id': str(i),
    #             'name': 'ldjson_'+str(i),
    #             'count_of_something': i*i
    #         }
    #         file.write(json.dumps(obj)+'\n')


    data = []
    with open(DICT_SETTINGS_VIEWER['data_path'], 'r') as file:
        for row in file:
            obj = json.loads(row)
            tmp = {}
            for field in DICT_SETTINGS_VIEWER['data_structure']:
                tmp[field] = obj[field]
            data.append(tmp)
    return data

def index_example_data():
    model_custom.objects.all().delete()
    m_Entity.objects.all().delete()
    m_Tag.objects.all().delete()
    list_entries = []
    for i in range(2000):
        list_entries.append(model_custom(name='name'+str(i), count_of_something=i))

    model_custom.objects.bulk_create(list_entries)

def set_sessions(request):
    set_session(request, 'is_collapsed_div_filters', default=True)
    set_session(request, 'is_collapsed_div_tags', default=True)
    set_session(request, 'is_collapsed_div_settings', default=True)
    set_session(request, 'viewer__selected_tags', default=[])

    set_session_from_url(request, 'viewer__page', default=1)

    set_session_from_url(request, 'viewer__columns', default=DICT_SETTINGS_VIEWER['displayed_fields'] + ['viewer__item_selection', 'viewer__tags'], is_json=True)
    set_session_from_url(request, 'viewer__filter_tags', default=[], is_json=True)

    set_session_from_url(request, 'viewer__filter_custom', default={obj_filter['data_field']:obj_filter['default_value'] for obj_filter in DICT_SETTINGS_VIEWER['filters']}, is_json=True)
    
    # in case of newly added filters add them
    dict_tmp = {obj_filter['data_field']:obj_filter['default_value'] for obj_filter in DICT_SETTINGS_VIEWER['filters']}
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

def get_setting(key):
    if key in DICT_SETTINGS_VIEWER:
        return DICT_SETTINGS_VIEWER[key]

    if key == 'use_cache':
        return False;
    elif key == 'page_size':
        return 25;

    raise ValueError('setting-key \''+key+'\' not found')

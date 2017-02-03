import time
import json
import csv
import importlib
from collections import OrderedDict
from settings_viewer import DICT_SETTINGS_VIEWER
from viewer.models import m_Tag, m_Entity
from django.apps import apps
module_custom = importlib.import_module(DICT_SETTINGS_VIEWER['app_label']+'.models')
model_custom = getattr(module_custom, DICT_SETTINGS_VIEWER['model_name'])

def get_or_create_tag(name, defaults={}):
    name = name.strip()
    name = name.replace(' ', '-')
    db_obj_tag = m_Tag.objects.get_or_create(name=name, defaults=defaults)
    return db_obj_tag

def load_data():
    data = []
    data_only_ids = []
    dict_ids = {}

    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        data = model_custom.objects.all()
        data_only_ids = [str(getattr(entity, DICT_SETTINGS_VIEWER['id'])) for entity in model_custom.objects.all().only(DICT_SETTINGS_VIEWER['id'])]
    elif DICT_SETTINGS_VIEWER['data_type'] == 'csv-file':
        data = load_file_csv()
        data_only_ids = [str(item[DICT_SETTINGS_VIEWER['id']]) for item in data]
        dict_ids = {str(item[DICT_SETTINGS_VIEWER['id']]):index for index, item in enumerate(data)}
    elif DICT_SETTINGS_VIEWER['data_type'] == 'ldjson-file':
        data = load_file_ldjson()
        data_only_ids = [str(item[DICT_SETTINGS_VIEWER['id']]) for item in data]
        dict_ids = {str(item[DICT_SETTINGS_VIEWER['id']]):index for index, item in enumerate(data)}

    return data, data_only_ids, dict_ids

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
    #     for i in range(1000):
    #         obj = {
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

def set_session(request, key, default):
    sessionkey = 'viewer__'+key
    if sessionkey not in request.session:
        request.session[sessionkey] = default

def set_session_from_url(request, key, default, is_array=False):
    sessionkey = 'viewer__'+key

    if request.GET.get(key) != None:
        if is_array:
            request.session[sessionkey] = json.loads(request.GET.get(key))
        else:
            request.session[sessionkey] = request.GET.get(key)
    else:
        if sessionkey not in request.session:
            request.session[sessionkey] = default

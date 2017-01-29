import time
import json
import csv
from collections import OrderedDict
from settings_viewer import DICT_SETTINGS_VIEWER
from viewer.models import m_Tag, m_Entity, Example_Model

def get_or_create_tag(name, defaults={}):
    name = name.strip()
    name = name.replace(' ', '-')
    db_obj_tag = m_Tag.objects.get_or_create(name=name, defaults=defaults)
    return db_obj_tag

def load_data():
    data = []
    data_only_ids = []
    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        db_model = apps.get_model(DICT_SETTINGS_VIEWER['app_label'], DICT_SETTINGS_VIEWER['model_name'])
        data = db_model.objects.all()
        data_only_ids = [str(getattr(entity, DICT_SETTINGS_VIEWER['id'])) for entity in db_model.objects.all().only(DICT_SETTINGS_VIEWER['id'])]
    elif DICT_SETTINGS_VIEWER['data_type'] == 'csv-file':
        data = load_file_csv()
        data_only_ids = [str(item[DICT_SETTINGS_VIEWER['id']]) for item in data]
    elif DICT_SETTINGS_VIEWER['data_type'] == 'ldjson-file':
        data = load_file_ldjson()
        data_only_ids = [str(item[DICT_SETTINGS_VIEWER['id']]) for item in data]


    return data, data_only_ids

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
    list_entries = []
    for i in range(1000):
        list_entries.append(Example_Model(name='name'+str(i), count_of_something=i))

    Example_Model.objects.bulk_create(list_entries)

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

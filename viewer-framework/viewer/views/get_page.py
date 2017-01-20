from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render
from django.apps import apps
from django.template import Engine, Context
from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

glob_page_size = 25

def get_page(request):
    # request.session.flush()
##### handle session entries
    for viewer__filter in  DICT_SETTINGS_VIEWER['filters']:
        if viewer__filter['type'] == 'text':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_name'], viewer__filter['default_value'])
        elif viewer__filter['type'] == 'checkbox':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_name'], True if viewer__filter['default_value'] == 'checked' else False)


    set_session_from_url(request, 'viewer__page', 1)
##### load data and apply filters
    data = []
    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        db_model = apps.get_model(DICT_SETTINGS_VIEWER['app_label'], DICT_SETTINGS_VIEWER['model_name'])
        data = db_model.objects.all()
    elif DICT_SETTINGS_VIEWER['data_type'] == 'csv-file':
        data = load_file_csv()
    elif DICT_SETTINGS_VIEWER['data_type'] == 'ldjson-file':
        data = load_file_ldjson()

##### page the dataset
    paginator = Paginator(data, glob_page_size)
    try:
        data = paginator.page(request.session['viewer__viewer__page'])
        # data = paginator.page(request.session['index__current_page'])
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        data = paginator.page(paginator.num_pages)

##### handle post requests
    context = {}
    context['settings'] = DICT_SETTINGS_VIEWER
    context['data'] = data

    previous_page_number = None
    next_page_number = None
    if data.has_previous():
        previous_page_number = data.previous_page_number()
    if data.has_next():
        next_page_number = data.next_page_number()

    template = get_template('viewer/table.html')
    return JsonResponse({'content':template.render(context, request),
            # 'tags':[ {'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in set_tags],
            'count_pages':data.paginator.num_pages,
            'count_entries':data.paginator.count,
            'previous_page_number':previous_page_number,
            'next_page_number':next_page_number
        })

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
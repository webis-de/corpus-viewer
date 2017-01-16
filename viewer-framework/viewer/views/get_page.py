from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render
from django.apps import apps
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

glob_page_size = 25

def get_page(request):
    # index_example_data()
    # request.session.flush()
##### handle session entries
    for viewer__filter in  DICT_SETTINGS_VIEWER['filters']:
        if viewer__filter['type'] == 'text':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_id'], viewer__filter['default_value'])
        elif viewer__filter['type'] == 'checkbox':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_id'], True if viewer__filter['default_value'] == 'checked' else False)

    set_session(request, 'is_collapsed_div_filters', True)

##### load data and apply filters
    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        db_model = apps.get_model(DICT_SETTINGS_VIEWER['app_label'], DICT_SETTINGS_VIEWER['model_name'])
        data = db_model.objects.all()


    elif DICT_SETTINGS_VIEWER['data_type'] == 'csv-file':
        pass
    elif DICT_SETTINGS_VIEWER['data_type'] == 'ldjson-file':
        pass

##### page the dataset
    paginator = Paginator(data, glob_page_size)
    try:
        data = paginator.page(1)
        # data = paginator.page(request.session['index__current_page'])
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        data = paginator.page(paginator.num_pages)

##### handle post requests
    # print(DICT_SETTINGS_VIEWER)
    
    context = {}
    context['settings'] = DICT_SETTINGS_VIEWER
    context['data'] = data
    return render(request, 'viewer/table.html', context)

def load_file_csv():
    pass

def load_file_ldjson():
    pass
# 
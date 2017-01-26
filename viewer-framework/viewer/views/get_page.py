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
    # this seems to be redundant
    set_session_from_url(request, 'viewer__page', 1)

    for viewer__filter in  DICT_SETTINGS_VIEWER['filters']:
        if viewer__filter['type'] == 'text':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_name'], viewer__filter['default_value'])
        elif viewer__filter['type'] == 'checkbox':
            set_session_from_url(request, 'filter_'+viewer__filter['data_field_name'], True if viewer__filter['default_value'] == 'checked' else False)

##### load data and apply filters
    data, data_only_ids = load_data()

    list_tags = get_set_tags_filtered_items(data_only_ids)

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

    add_tags(data)
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
            'tags_filtered_items': list_tags,
            'count_pages': data.paginator.num_pages,
            'count_entries': data.paginator.count,
            'previous_page_number': previous_page_number,
            'next_page_number': next_page_number
        })

def get_set_tags_filtered_items(list_ids):
    n = 100
    chunks = [list_ids[x:x+n] for x in range(0, len(list_ids), n)]

    list_tags = []
    for chunk in chunks:
        list_tags += m_Tag.objects.filter(m2m_entity__in=chunk).distinct()
    
    dict_ordered_tags = OrderedDict()
    for tag in list_tags:
        if tag.name not in dict_ordered_tags:
            dict_ordered_tags[tag.name] = {'id': tag.id, 'name': tag.name, 'color': tag.color}

    return list(dict_ordered_tags.values())

def add_tags(data):
    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        for item in data:
            item.tags = []
    else:
        list_ids = [item[DICT_SETTINGS_VIEWER['id']] for item in data]
        db_obj_entities = m_Entity.objects.filter(id_item__in=list_ids).prefetch_related('tags')
        dict_entities = {entity.id_item: entity for entity in db_obj_entities}

        for item in data:
            try:
                item['tags'] = dict_entities[str(item[DICT_SETTINGS_VIEWER['id']])].tags.all()
            except KeyError:
                # if there is no entity entry in the database
                item['tags'] = []
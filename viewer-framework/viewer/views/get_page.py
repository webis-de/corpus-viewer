from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render
from django.template import Engine, Context
from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def get_page(request):
##### handle session entries
    set_sessions(request)
##### load data and apply filters
    data, data_only_ids = get_filtered_data(request)
    # list_tags = get_tags_filtered_items(data_only_ids, request)
    list_tags = []
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'add_tag':
            response['data'] = add_tag(obj, data)
        return JsonResponse(response)
##### page the dataset
    paginator = Paginator(data, get_setting('page_size'))
    try:
        data = paginator.page(request.session['viewer__viewer__page'])
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        data = paginator.page(paginator.num_pages)
##### add tags to the dataset
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

def get_filtered_data(request):
    data, data_only_ids, dict_ids = load_data()
    #
    # FILTER BY TAGS
    #
    if len(request.session['viewer__viewer__filter_tags']) > 0:
        if DICT_SETTINGS_VIEWER['data_type'] == 'database':

            for tag in request.session['viewer__viewer__filter_tags']:
                data = data.filter(viewer_tags__name=tag)
        else:
            data = filter_data_tags(data, request.session['viewer__viewer__filter_tags'])
    #
    # FILTERS
    #
    for obj_filter in DICT_SETTINGS_VIEWER['filters']:
        data = filter_data(request, data, obj_filter)
    #
    # UPDATE data_only_ids
    #
    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        data_only_ids = [item.id for item in data]
    else:
        data_only_ids = [item[DICT_SETTINGS_VIEWER['id']] for item in data]

    return data, data_only_ids

def filter_data(request, data, obj_filter):
    value = request.session['viewer__viewer__filter_custom'][obj_filter['data_field']]
    if value != '':
        if DICT_SETTINGS_VIEWER['data_type'] == 'database':
            data = data.filter(**{obj_filter['data_field']+'__icontains': value})
        else:
            data = [item for item in data if value in item[obj_filter['data_field']]]

    return data

def filter_data_tags(data, list_tags):
    queryset_tags = m_Tag.objects.filter(name__in=list_tags).prefetch_related('m2m_entity')

    for db_obj_tag in queryset_tags:
        list_ids = [entity.id_item for entity in db_obj_tag.m2m_entity.all()]
        data = [item for item in data if str(item[DICT_SETTINGS_VIEWER['id']]) in list_ids]

    return data

def add_tag(obj, data):
    [db_obj_tag, created_tag] = get_or_create_tag(obj['tag'], defaults={'color': obj['color']})

    entities = []
    if obj['ids'] == 'all':
        entities = data
    else:
        entities = list(model_custom.objects.filter(post_id_str__in=obj['ids']))

    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        n = 900
        chunks = [entities[x:x+n] for x in range(0, len(entities), n)]
        for chunk in chunks:
            db_obj_tag.m2m_custom_model.add(*chunk)
    else:

        index_missing_entities(entities)

        n = 900
        chunks = [entities[x:x+n] for x in range(0, len(entities), n)]
        for chunk in chunks:
            db_obj_entities = m_Entity.objects.filter(id_item__in=chunk)
            db_obj_tag.m2m_entity.add(*db_obj_entities)

    if db_obj_tag.color != obj['color']:
        db_obj_tag.color = obj['color']
        db_obj_tag.save()

    return {'created_tag': created_tag, 'tag': {'id': db_obj_tag.id, 'name': db_obj_tag.name, 'color': db_obj_tag.color} }

def index_missing_entities(entities):
    queryset = m_Entity.objects.all()
    set_new_entities = set(entities)

    set_new_entities.difference_update({entity.id_item for entity in queryset})

    if len(set_new_entities) > 0:
        m_Entity.objects.bulk_create([m_Entity(id_item=entity) for entity in set_new_entities])


def get_tags_filtered_items(list_ids, request):
    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        list_tags = []
        n = 900
        chunks = [list_ids[x:x+n] for x in range(0, len(list_ids), n)]
        for chunk in chunks:
            list_tags += m_Tag.objects.filter(m2m_custom_model__in=chunk).distinct()


        dict_ordered_tags = OrderedDict()
        for tag in list_tags:
            if tag.name not in dict_ordered_tags:
                dict_ordered_tags[tag.name] = {'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_selected': str(tag.id) in request.session['viewer__viewer__selected_tags']}
        return list(dict_ordered_tags.values())
    else:
        n = 900
        chunks = [list_ids[x:x+n] for x in range(0, len(list_ids), n)]

        list_tags = []
        for chunk in chunks:
            list_tags += m_Tag.objects.filter(m2m_entity__in=chunk).distinct()

        dict_ordered_tags = OrderedDict()
        for tag in list_tags:
            if tag.name not in dict_ordered_tags:
                dict_ordered_tags[tag.name] = {'id': tag.id, 'name': tag.name, 'color': tag.color, 'is_selected': str(tag.id) in request.session['viewer__viewer__selected_tags']}

        return list(dict_ordered_tags.values())

def add_tags(data):
    if DICT_SETTINGS_VIEWER['data_type'] != 'database':
        list_ids = [item[DICT_SETTINGS_VIEWER['id']] for item in data]
        db_obj_entities = m_Entity.objects.filter(id_item__in=list_ids).prefetch_related('viewer_tags')
        dict_entities = {entity.id_item: entity for entity in db_obj_entities}

        for item in data:
            try:
                item['viewer_tags'] = dict_entities[str(item[DICT_SETTINGS_VIEWER['id']])].viewer_tags.all()
            except KeyError:
                # if there is no entity entry in the database
                item['viewer_tags'] = []
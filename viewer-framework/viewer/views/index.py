from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_session_entry':
            request.session['viewer__'+obj['session_key']] = obj['session_value']
            response['status'] = 'success'
        elif obj['task'] == 'add_tag':
            add_tag(obj)
        return JsonResponse(response)
    # index_example_data()
    # request.session.flush()
    set_session(request, 'is_collapsed_div_filters', True)
    set_session(request, 'is_collapsed_div_tags', True)
    set_session_from_url(request, 'viewer__columns', DICT_SETTINGS_VIEWER['displayed_fields'] + ['viewer__item_selection', 'viewer__tags'], is_array=True)

    context = {}
    context['json_url_params'] = json.dumps(get_url_params(request))
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)

def add_tag(obj):
    db_obj_tag = get_tag(obj['tag'], defaults={'color': obj['color']})

    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        print('not implemented')
    else:
        entities = []
        if obj['ids'] == 'all':
            tmp, entities = load_data()
        else:
            entities = obj['ids']

        index_missing_entities(entities)

        db_obj_entities = m_Entity.objects.filter(id_item__in=entities)
        db_obj_tag.m2m_entity.add(*db_obj_entities)

    if db_obj_tag.color != obj['color']:
        db_obj_tag.color = obj['color']
        db_obj_tag.save()

def index_missing_entities(entities):
    queryset = m_Entity.objects.all()
    set_new_entities = set(entities)

    set_new_entities.difference_update({entity.id_item for entity in queryset})

    if len(set_new_entities) > 0:
        m_Entity.objects.bulk_create([m_Entity(id_item=entity) for entity in set_new_entities])

def get_url_params(request):
    dict_url_params = request.GET.copy()

    if 'viewer__columns' in dict_url_params:
        dict_url_params['viewer__columns'] = json.loads(dict_url_params['viewer__columns'])
    else:
        set_tmp = set(request.session['viewer__viewer__columns'])
        dict_url_params['viewer__columns'] = request.session['viewer__viewer__columns']

    return dict_url_params

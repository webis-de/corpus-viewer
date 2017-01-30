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
            response['data'] = add_tag(obj)
        elif obj['task'] == 'get_tag_recommendations':
            array_tag_recommendations = get_tag_recommendations(request, obj)
            response['status'] = 'success'
            response['data'] = {'array_recommendations':array_tag_recommendations}
        return JsonResponse(response)
    # index_example_data()
    # request.session.flush()
    print(request.session.items())
    set_session(request, 'is_collapsed_div_filters', True)
    set_session(request, 'is_collapsed_div_tags', True)
    set_session(request, 'viewer__selected_tags', [])

    # this seems to be redundant
    set_session_from_url(request, 'viewer__page', 1)
    set_session_from_url(request, 'viewer__columns', DICT_SETTINGS_VIEWER['displayed_fields'] + ['viewer__item_selection', 'viewer__tags'], is_array=True)
    set_session_from_url(request, 'viewer__filter_tags', [], is_array=True)

    context = {}
    context['json_url_params'] = json.dumps(get_url_params(request))
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)


def get_tag_recommendations(request, obj):
    array_tag_recommendations = []
    array_tags = m_Tag.objects.filter(name__contains=obj['tag_name'])

    for tag in array_tags:
        array_tag_recommendations.append({'name':tag.name, 'color':tag.color});

    return array_tag_recommendations

def add_tag(obj):
    [db_obj_tag, created_tag] = get_or_create_tag(obj['tag'], defaults={'color': obj['color']})

    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        print('not implemented')
    else:
        entities = []
        if obj['ids'] == 'all':
            tmp, entities = load_data()
        else:
            entities = obj['ids']

        index_missing_entities(entities)

        n = 100
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

def get_url_params(request):
    dict_url_params = request.GET.copy()

    if 'viewer__page' in dict_url_params:
        dict_url_params['viewer__page'] = dict_url_params['viewer__page']
    else:
        dict_url_params['viewer__page'] = request.session['viewer__viewer__page']

    if 'viewer__columns' in dict_url_params:
        dict_url_params['viewer__columns'] = json.loads(dict_url_params['viewer__columns'])
    else:
        dict_url_params['viewer__columns'] = request.session['viewer__viewer__columns']

    if 'viewer__filter_tags' in dict_url_params:
        dict_url_params['viewer__filter_tags'] = json.loads(dict_url_params['viewer__filter_tags'])
    else:
        dict_url_params['viewer__filter_tags'] = request.session['viewer__viewer__filter_tags']

    return dict_url_params

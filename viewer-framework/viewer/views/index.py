from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
##### set sessions
    # request.session.flush()
    set_sessions(request)
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_session_entry':
            request.session['viewer__'+obj['session_key']] = obj['session_value']
            response['status'] = 'success'
        elif obj['task'] == 'get_tag_recommendations':
            array_tag_recommendations = get_tag_recommendations(request, obj)
            response['status'] = 'success'
            response['data'] = {'array_recommendations':array_tag_recommendations}
        elif obj['task'] == 'delete_tag_from_item':
            response = delete_tag_from_item(obj)

        return JsonResponse(response)

    # index_example_data()

    context = {}
    context['json_url_params'] = json.dumps(get_url_params(request))
    context['json_filters'] = json.dumps(DICT_SETTINGS_VIEWER['filters'])
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)

def delete_tag_from_item(obj):
    response = {}

    db_obj_tag = m_Tag.objects.get(id=obj['id_tag'])
    if DICT_SETTINGS_VIEWER['data_type'] == 'database':
        db_obj_item = model_custom.objects.get(**{DICT_SETTINGS_VIEWER['id']: obj['id_item']})
        db_obj_tag.m2m_custom_model.remove(db_obj_item)
        response['status'] = 'success'
    else:
        print('TO BE IMPLEMENTED')


    return response

def get_tag_recommendations(request, obj):
    array_tag_recommendations = []
    array_tags = m_Tag.objects.filter(name__contains=obj['tag_name'])

    for tag in array_tags:
        array_tag_recommendations.append({'name':tag.name, 'color':tag.color});

    return array_tag_recommendations

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

    if 'viewer__filter_custom' in dict_url_params:
        dict_url_params['viewer__filter_custom'] = json.loads(dict_url_params['viewer__filter_custom'])
    else:
        dict_url_params['viewer__filter_custom'] = request.session['viewer__viewer__filter_custom']

    return dict_url_params

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
        elif obj['task'] == 'get_tag_recommendations':
            array_tag_recommendations = get_tag_recommendations(request, obj)
            response['status'] = 'success'
            response['data'] = {'array_recommendations':array_tag_recommendations}
        return JsonResponse(response)
        
    # index_example_data()
    # request.session.flush()

    set_session(request, 'is_collapsed_div_filters', True)
    set_session(request, 'is_collapsed_div_tags', True)
    set_session(request, 'viewer__selected_tags', [])
    set_session_from_url(request, 'viewer__filter_custom', {obj_filter['data_field']:obj_filter['default_value'] for obj_filter in DICT_SETTINGS_VIEWER['filters']}, is_array=True)

    # this seems to be redundant
    set_session_from_url(request, 'viewer__page', 1)
    set_session_from_url(request, 'viewer__columns', DICT_SETTINGS_VIEWER['displayed_fields'] + ['viewer__item_selection', 'viewer__tags'], is_array=True)
    set_session_from_url(request, 'viewer__filter_tags', [], is_array=True)

    # for obj_filter in DICT_SETTINGS_VIEWER['filters']:
    #     set_session_from_url(request, 'viewer__filter_custom_'+obj_filter['data_field'], obj_filter['default_value'])

    for key, value in request.session.items():
        print(key, value)

    context = {}
    context['json_url_params'] = json.dumps(get_url_params(request))
    context['json_filters'] = json.dumps(DICT_SETTINGS_VIEWER['filters'])
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)


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

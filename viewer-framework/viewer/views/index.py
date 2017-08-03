from .shared_code import set_sessions, glob_manager_data, get_current_corpus
from django.http import JsonResponse
from django.shortcuts import render, redirect
from viewer.models import m_Tag, m_Entity
import json
from threading import Thread

def index(request):
##### set sessions
    try:
        set_sessions(request)
    except:
        if request.is_ajax():
            raise Http404("Corpus does not exist")

        return redirect('dashboard:index')

    id_corpus = get_current_corpus(request)

    state_loaded = glob_manager_data.get_state_loaded(id_corpus)
    if state_loaded != glob_manager_data.State_Loaded.LOADED:
        context = {}
        context['id_corpus'] = id_corpus
        context['state_loaded'] = state_loaded
        try:
            context['number_of_indexed_items'] = glob_manager_data.get_number_of_indexed_items(id_corpus)
        except:
            context['number_of_indexed_items'] = 0

        context['handle_incides'] = glob_manager_data.get_active_handle_indices()
        context['settings'] = glob_manager_data.get_settings_for_corpus(id_corpus)
        return render(request, 'viewer/not_loaded.html', context)
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_session_entry':
            request.session[id_corpus]['viewer__'+obj['session_key']] = obj['session_value']
            request.session.modified = True
            response['status'] = 'success'
        elif obj['task'] == 'get_tag_recommendations':
            array_tag_recommendations = get_tag_recommendations(request, obj)
            response['status'] = 'success'
            response['data'] = {'array_recommendations':array_tag_recommendations}
        elif obj['task'] == 'delete_tag_from_item':
            response = delete_tag_from_item(obj, request)
        elif obj['task'] == 'toggle_item_to_tag':
            response = toggle_item_to_tag(obj, request)
        elif obj['task'] == 'check_if_tag_exists':
            response = check_if_tag_exists(obj, request)
        elif obj['task'] == 'get_handle_indices':
            response['data'] = glob_manager_data.get_active_handle_indices()

        return JsonResponse(response)

    # index_example_data()
    # print('final value: '+str(request.session[id_corpus]['viewer__settings_viewer_large_corpus']))
    context = {}
    context['json_url_params'] = json.dumps(get_url_params(request))
    context['json_filters'] = json.dumps(glob_manager_data.get_setting_for_corpus('filters', id_corpus))
    context['settings'] = glob_manager_data.get_settings_for_corpus(id_corpus)
    return render(request, 'viewer/index.html', context)

def check_if_tag_exists(obj, request):
    response = {}
    response['data'] = {}

    try:
        db_obj_tag = m_Tag.objects.get(name=obj['name'], key_corpus=get_current_corpus(request))
        response['data']['tag'] = {'id':db_obj_tag.id ,'name':db_obj_tag.name, 'color':db_obj_tag.color}
        response['data']['exists'] = True
    except:
        response['data']['exists'] = False

    return response

def toggle_item_to_tag(obj, request):
    response = {}
    response['data'] = {}
    db_obj_tag = m_Tag.objects.get(id=obj['id_tag'])

    if get_setting('data_type', request=request) == 'database':
        print('TO BE IMPLEMENTED')
    else:
        print(str(obj['id_item']))
        try:
            db_obj_entity = m_Entity.objects.get(id_item=str(obj['id_item']), key_corpus=get_current_corpus(request))
            
            if m_Tag.objects.filter(pk=obj['id_tag'], m2m_entity__pk=db_obj_entity.pk).exists():
                response['data']['removed'] = True
                db_obj_tag.m2m_entity.remove(db_obj_entity)
            else:
                db_obj_tag.m2m_entity.add(db_obj_entity)
                response['data']['removed'] = False
        except m_Entity.DoesNotExist:
            response['data']['removed'] = False
            db_obj_entity = m_Entity.objects.create(id_item=str(obj['id_item']), key_corpus=get_current_corpus(request))
            db_obj_tag.m2m_entity.add(db_obj_entity)

    return response

def delete_tag_from_item(obj, request):
    response = {}

    db_obj_tag = m_Tag.objects.get(id=obj['id_tag'])
    if get_setting('data_type', request=request) == 'database':
        db_obj_item = model_custom.objects.get(**{get_setting('id', request=request): obj['id_item']})
        db_obj_tag.m2m_custom_model.remove(db_obj_item)
        response['status'] = 'success'
    else:
        print('TO BE IMPLEMENTED')


    return response

def get_tag_recommendations(request, obj):
    array_tag_recommendations = []
    array_tags = m_Tag.objects.filter(name__contains=obj['tag_name'], key_corpus=get_current_corpus(request))

    for tag in array_tags:
        array_tag_recommendations.append({'id':tag.id ,'name':tag.name, 'color':tag.color});

    return array_tag_recommendations

def get_url_params(request):
    dict_url_params = request.GET.copy()

    if 'viewer__page' in dict_url_params:
        dict_url_params['viewer__page'] = dict_url_params['viewer__page']
    else:
        dict_url_params['viewer__page'] = request.session[get_current_corpus(request)]['viewer__viewer__page']

    if 'viewer__current_corpus' in dict_url_params:
        dict_url_params['viewer__current_corpus'] = dict_url_params['viewer__current_corpus']
    else:
        dict_url_params['viewer__current_corpus'] = get_current_corpus(request)

    if 'viewer__columns' in dict_url_params:
        dict_url_params['viewer__columns'] = json.loads(dict_url_params['viewer__columns'])
    else:
        dict_url_params['viewer__columns'] = request.session[get_current_corpus(request)]['viewer__viewer__columns']

    if 'viewer__sorted_columns' in dict_url_params:
        dict_url_params['viewer__sorted_columns'] = json.loads(dict_url_params['viewer__sorted_columns'])
    else:
        dict_url_params['viewer__sorted_columns'] = request.session[get_current_corpus(request)]['viewer__viewer__sorted_columns']

    if 'viewer__filter_tags' in dict_url_params:
        dict_url_params['viewer__filter_tags'] = json.loads(dict_url_params['viewer__filter_tags'])
    else:
        dict_url_params['viewer__filter_tags'] = request.session[get_current_corpus(request)]['viewer__viewer__filter_tags']

    if 'viewer__filter_custom' in dict_url_params:
        dict_url_params['viewer__filter_custom'] = json.loads(dict_url_params['viewer__filter_custom'])
    else:
        dict_url_params['viewer__filter_custom'] = request.session[get_current_corpus(request)]['viewer__viewer__filter_custom']

    return dict_url_params

def delete_session(request):
    request.session.flush()
    return JsonResponse({})
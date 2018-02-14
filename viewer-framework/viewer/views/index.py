from .shared_code import set_sessions, glob_manager_data, get_current_corpus, get_filters_if_not_empty
from django.http import JsonResponse
from django.shortcuts import render, redirect
from viewer.models import m_Tag, m_Entity
import json
import importlib
from threading import Thread
from django.conf import settings

def index(request, id_corpus):
##### set sessions
    # try:
    if not set_sessions(request, id_corpus):
        # exception = glob_manager_data.pop_exception(get_current_corpus(request))
        # print(exception)

        if request.is_ajax():
            raise Http404("Corpus does not exist")

        # if not get_current_corpus(request) in glob_manager_data.dict_exceptions:
        return redirect('dashboard:index')

    # id_corpus = get_current_corpus(request)

    if glob_manager_data.has_corpus_secret_token(id_corpus):
        try:
            secret_token = request.session[id_corpus]['viewer__secret_token']
        except KeyError:
            secret_token = None
        # secret_token = request.GET.get('secret_token')
        if not glob_manager_data.is_secret_token_valid(id_corpus, secret_token):
            # if request.is_ajax():
            #     raise Http404("Corpus does not exist")
            return redirect('viewer:add_token', id_corpus=id_corpus)       

##### check if has token for editing
    has_access_to_editing = glob_manager_data.get_has_access_to_editing(id_corpus, request)  

    state_loaded = glob_manager_data.get_state_loaded(id_corpus)
    if state_loaded != glob_manager_data.State_Loaded.LOADED:
        context = {}
        context['id_corpus'] = id_corpus
        context['state_loaded'] = state_loaded
        try:
            context['number_of_indexed_items'] = glob_manager_data.get_number_of_indexed_items(id_corpus)
        except:
            context['number_of_indexed_items'] = 0

        # if glob_manager_data.has_exception_for_corpus(id_corpus):
        context['exception'] = glob_manager_data.pop_exception(id_corpus)
        # else:
            # context['exception'] = ''

        context['handle_incides'] = glob_manager_data.get_active_handle_indices()
        context['settings'] = glob_manager_data.get_settings_for_corpus(id_corpus)
        context['id_corpus'] = id_corpus
        return render(request, 'viewer/not_loaded.html', context)
##### handle post requests
    if request.method == 'POST':
        response = {}
        obj = json.loads(request.body.decode("utf-8"))
        if obj['task'] == 'set_session_entry':
            if obj['session_key'] == 'dark_mode':
                request.session['viewer__'+obj['session_key']] = obj['session_value']
            else:
                request.session[id_corpus]['viewer__'+obj['session_key']] = obj['session_value']
                request.session.modified = True
            response['status'] = 'success'
        elif obj['task'] == 'get_tag_recommendations':
            array_tag_recommendations = get_tag_recommendations(request, obj)
            response['status'] = 'success'
            response['data'] = {'array_recommendations':array_tag_recommendations}
        elif obj['task'] == 'delete_tag_from_item':
            if has_access_to_editing:
                response = delete_tag_from_item(obj, id_corpus)
        elif obj['task'] == 'toggle_item_to_tag':
            if has_access_to_editing:
                response = toggle_item_to_tag(obj, id_corpus)
        elif obj['task'] == 'check_if_tag_exists':
            if has_access_to_editing:
                response = check_if_tag_exists(obj, request)
        elif obj['task'] == 'get_handle_indices':
            response['data'] = glob_manager_data.get_active_handle_indices()
        elif obj['task'] == 'submit_token_editing':
            input_secret_token = obj['token']
            request.session[id_corpus]['viewer__secret_token_editing'] = input_secret_token
            request.session.modified = True
            return redirect('viewer:index', id_corpus=id_corpus)


        return JsonResponse(response)

    # index_example_data()
    # print('final value: '+str(request.session[id_corpus]['viewer__settings_viewer_large_corpus']))
    context = {}
    dict_tmp = get_url_params(request)


    context['has_access_to_editing'] = has_access_to_editing

    context['are_filters_set'] = False if get_filters_if_not_empty(request, id_corpus) == None else True

    context['json_url_params'] = json.dumps(dict_tmp)
    context['tag_filter_active'] = json.dumps(get_tag_filter_active(id_corpus, dict_tmp['viewer__filter_tags']))
    context['json_filters'] = json.dumps(glob_manager_data.get_setting_for_corpus('filters', id_corpus))
    context['settings'] = glob_manager_data.get_settings_for_corpus(id_corpus)
    context['id_corpus'] = id_corpus
    context['name_corpus'] = glob_manager_data.get_setting_for_corpus('name', id_corpus)
    context['mode_navbar'] = 'viewer'

    try:
        context['is_dashboard_available'] = settings.DASHBOARD_AVAILABLE
    except AttributeError:
        context['is_dashboard_available'] = False

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

def toggle_item_to_tag(obj, id_corpus):
    response = {}
    response['data'] = {}
    db_obj_tag = m_Tag.objects.get(id=obj['id_tag'])

    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        db_obj_tag = m_Tag.objects.get(id=obj['id_tag'])

        module_custom = importlib.import_module(glob_manager_data.get_setting_for_corpus('app_label', id_corpus)+'.models')
        model_custom = getattr(module_custom, glob_manager_data.get_setting_for_corpus('model_name', id_corpus))

        related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)
        getattr(db_obj_tag, related_name).add(model_custom.objects.get(id=obj['viewer__id_item_internal']))
    else:
        print(str(obj['id_item']))
        try:
            db_obj_entity = m_Entity.objects.get(id_item=str(obj['id_item']), key_corpus=id_corpus)
            
            if m_Tag.objects.filter(pk=obj['id_tag'], m2m_entity__pk=db_obj_entity.pk).exists():
                response['data']['removed'] = True
                db_obj_tag.m2m_entity.remove(db_obj_entity)
            else:
                db_obj_tag.m2m_entity.add(db_obj_entity)
                response['data']['removed'] = False
        except m_Entity.DoesNotExist:
            response['data']['removed'] = False
            db_obj_entity = m_Entity.objects.create(
                id_item=str(obj['id_item']), 
                id_item_internal=str(obj['viewer__id_item_internal']), 
                key_corpus=id_corpus
            )
            
            db_obj_tag.m2m_entity.add(db_obj_entity)

    return response

def delete_tag_from_item(obj, id_corpus):
    response = {}

    db_obj_tag = m_Tag.objects.get(id=obj['id_tag'])
    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        module_custom = importlib.import_module(glob_manager_data.get_setting_for_corpus('app_label', id_corpus)+'.models')
        model_custom = getattr(module_custom, glob_manager_data.get_setting_for_corpus('model_name', id_corpus))

        related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)
        getattr(db_obj_tag, related_name).remove(model_custom.objects.get(id=obj['id_item']))
        
        response['status'] = 'success'
    else:
        db_obj_tag = m_Tag.objects.get(id=obj['id_tag'])
        db_obj_entity = m_Entity.objects.get(id_item=str(obj['id_item']), key_corpus=id_corpus)

        db_obj_tag.m2m_entity.remove(db_obj_entity)
        response['status'] = 'success'


    return response

def get_tag_recommendations(request, obj):
    array_tag_recommendations = []
    array_tags = m_Tag.objects.filter(name__contains=obj['tag_name'], key_corpus=get_current_corpus(request))

    for tag in array_tags:
        array_tag_recommendations.append({'id':tag.id ,'name':tag.name, 'color':tag.color});

    return array_tag_recommendations

def get_tag_filter_active(id_corpus, list_tags):
    dict_tags = {}
    queryset_tags = m_Tag.objects.filter(name__in=list_tags, key_corpus=id_corpus)
    for tag in queryset_tags:
        dict_tags[tag.name] = {'color': tag.color, 'name': tag.name, 'id': tag.id}

    return dict_tags

def get_url_params(request):
    dict_url_params = request.GET.copy()

    if 'viewer__page' in dict_url_params:
        dict_url_params['viewer__page'] = dict_url_params['viewer__page']
    else:
        dict_url_params['viewer__page'] = request.session[get_current_corpus(request)]['viewer__viewer__page']

    # if 'viewer__current_corpus' in dict_url_params:
    #     dict_url_params['viewer__current_corpus'] = dict_url_params['viewer__current_corpus']
    # else:
    #     dict_url_params['viewer__current_corpus'] = get_current_corpus(request)

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
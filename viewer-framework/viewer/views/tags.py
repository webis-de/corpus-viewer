from .shared_code import get_current_corpus, glob_manager_data
from .get_page import index_missing_entities
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from viewer.models import m_Tag, m_Entity
import json
import os
import importlib
import time

def tags_export(request, id_corpus):
    json_result = ''
    queryset_tags = m_Tag.objects.filter(key_corpus=id_corpus)
    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
        related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)
        queryset_tags = queryset_tags.prefetch_related(related_name)
    else:
        queryset_tags = queryset_tags.prefetch_related('m2m_entity')
    for tag in queryset_tags:
        obj_tag = {}
        obj_tag['name'] = tag.name
        obj_tag['color'] = tag.color
        list_ids = []
        if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
            related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)

            for entity in getattr(tag, related_name).all():
                list_ids.append(entity.id)
        else:
            for entity in tag.m2m_entity.all():
                list_ids.append(entity.id_item)

        obj_tag['ids'] = list_ids
        json_result += json.dumps(obj_tag) + '\n'

    response = HttpResponse(json_result, content_type="text/json")
    response['Content-Disposition'] = 'attachment; filename=' + 'tags_{}_.json'.format(id_corpus)
    return response

def tags(request, id_corpus):
    tags = m_Tag.objects.filter(key_corpus=id_corpus)


    # with open('int.bin', 'w') as f:
    #     for x in range(0, 20 * 100 000 000):
    #             f.write(1)

    if request.method == 'POST':
        try:
            cookie_id = request.COOKIES['csrftoken']
            response = {}
            obj = json.loads(request.body.decode("utf-8"))
            if obj['task'] == 'set_session_entry':
                if obj['session_key'] == 'dark_mode':
                    request.session['viewer__'+obj['session_key']] = obj['session_value']
                else:
                    request.session[id_corpus]['viewer__'+obj['session_key']] = obj['session_value']
                    request.session.modified = True
                response['status'] = 'success'
            elif obj['task'] == 'update_name':
                response = update_name(obj, request)
            elif obj['task'] == 'merge_tags':
                response['data'] = merge_tags(obj)
            elif obj['task'] == 'update_color':
                response = update_color(obj)
            elif obj['task'] == 'delete_tag':
                response = delete_tag(obj)
            elif obj['task'] == 'export_tags':
                response = export_tags(obj, request)
            elif obj['task'] == 'add_items':
                response = add_items(obj, request)
        except:
            response = import_tags(request, id_corpus)


        return JsonResponse(response)

    context = {}
    
    context['id_corpus'] = id_corpus
    context['name_corpus'] = glob_manager_data.get_setting_for_corpus('name', id_corpus)
    context['data_type'] = glob_manager_data.get_setting_for_corpus('data_type', id_corpus)
    context['mode_navbar'] = 'tags'
    context['tags'] = tags
    if request.is_ajax():
        return render(request, 'viewer/tags.html', context)
    else:
        return render(request, 'viewer/tags.html', context)

def add_items(obj, request):
    response = {}

    
    print(obj)

    return response

def import_tags(request, id_corpus):
    response = {}

    if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) != 'database':
        dict_ids_to_ids_internal = glob_manager_data.get_dict_ids_to_ids_internal(id_corpus)
    else:
        module_custom = importlib.import_module(glob_manager_data.get_setting_for_corpus('app_label', id_corpus)+'.models')
        model_custom = getattr(module_custom, glob_manager_data.get_setting_for_corpus('model_name', id_corpus))

    for line in request.FILES['file'].read().decode('utf-8').strip().split('\n'):
        obj_json = json.loads(line)
        obj_tag = m_Tag.objects.get_or_create(name = obj_json['name'], key_corpus=id_corpus, color = obj_json['color'])[0]
        
        if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
            related_name = glob_manager_data.get_setting_for_corpus('database_related_name', id_corpus)

            ThroughModel = getattr(m_Tag, related_name).through
            list_tmp = []

            for id_item in obj_json['ids']:
                obj_db_entity = model_custom.objects.get(id=id_item)
                list_tmp.append(ThroughModel(**{
                    'm_tag_id': obj_tag.pk, 
                    glob_manager_data.get_setting_for_corpus('model_name', id_corpus).lower()+'_id': obj_db_entity.pk
                }))

            ThroughModel.objects.bulk_create(list_tmp)
        else:
            ThroughModel = m_Tag.m2m_entity.through
            list_tmp = []

            print(obj_json['ids'])

            entities = []

            for id_item in obj_json['ids']:
                entities.append({'id_item': id_item, 'viewer__id_item_internal': dict_ids_to_ids_internal[id_item]})


            index_missing_entities(entities, id_corpus)

            for id_item in obj_json['ids']:
                obj_db_entity = m_Entity.objects.get(id_item=id_item, key_corpus=id_corpus)
                list_tmp.append(ThroughModel(m_tag_id=obj_tag.pk, m_entity_id=obj_db_entity.pk))

            ThroughModel.objects.bulk_create(list_tmp)
    
    return response
    # response = {}
    
    # dict_ids_to_ids_internal = glob_manager_data.get_dict_ids_to_ids_internal(id_corpus)

    # if os.path.isfile(obj['path']):
    #     with open(obj['path'], 'r') as f:
    #         for line in f:
    #             obj_json = json.loads(line)

    #             obj_tag = m_Tag.objects.get_or_create(name = obj_json['name'], key_corpus=id_corpus, color = obj_json['color'])[0]

    #             if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
    #                 ThroughModel = m_Tag.m2m_custom_model.through
    #                 list_tmp = []

    #                 for id_item in obj_json['ids']:
    #                     obj_db_entity = model_custom.objects.get(id_item=id_item)
    #                     list_tmp.append(ThroughModel(**{
    #                         'm_tag_id': obj_tag.pk, 
    #                         glob_manager_data.get_setting_for_corpus('model_name', id_corpus).lower()+'_id': obj_db_entity.pk
    #                     }))

    #                 ThroughModel.objects.bulk_create(list_tmp)
    #             else:
    #                 ThroughModel = m_Tag.m2m_entity.through
    #                 list_tmp = []

    #                 print(obj_json['ids'])

    #                 entities = []

    #                 for id_item in obj_json['ids']:
    #                     entities.append({'id_item': id_item, 'viewer__id_item_internal': dict_ids_to_ids_internal[id_item]})


    #                 index_missing_entities(entities, id_corpus)

    #                 for id_item in obj_json['ids']:
    #                     obj_db_entity = m_Entity.objects.get(id_item=id_item, key_corpus=id_corpus)
    #                     list_tmp.append(ThroughModel(m_tag_id=obj_tag.pk, m_entity_id=obj_db_entity.pk))

    #                 ThroughModel.objects.bulk_create(list_tmp)

    # return response

# def export_tags(obj, request):
#     id_corpus = get_current_corpus(request)

#     response = {}

#     if obj['path'].strip() != '':
#         if not os.path.exists(obj['path']):
#             os.makedirs(obj['path'])
        
#     name_file = 'tags_exported_'+str(int(time.time()))+'.ldjson'
#     path_file = os.path.join(obj['path'], name_file)


#     with open(path_file, 'w') as f:
#         queryset_tags = m_Tag.objects.filter(key_corpus=id_corpus)
#         if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
#             queryset_tags = queryset_tags.prefetch_related('m2m_custom_model')
#         else:
#             queryset_tags = queryset_tags.prefetch_related('m2m_entity')
#         for tag in queryset_tags:
#             obj_tag = {}
#             obj_tag['name'] = tag.name
#             obj_tag['color'] = tag.color
#             list_ids = []
#             if glob_manager_data.get_setting_for_corpus('data_type', id_corpus) == 'database':
#                 for entity in tag.m2m_custom_model.all():
#                     list_ids.append(entity.id)
#             else:
#                 for entity in tag.m2m_entity.all():
#                     list_ids.append(entity.id_item)

#             obj_tag['ids'] = list_ids
#             f.write(json.dumps(obj_tag)+'\n')

#     return response

def delete_tag(obj):
    response = {}

    tag = m_Tag.objects.get(id=obj['id_tag'])
    tag.delete()

    return response

def merge_tags(obj):
    response = {}

    tag = m_Tag.objects.get(id=obj['id_tag'])

    existing_tag = m_Tag.objects.get(id=obj['existing_tag'])
    existing_tag.m2m_entity.add(*tag.m2m_entity.all())
    existing_tag.save()

    tag.delete()

    response['count_entities_updated'] = existing_tag.m2m_entity.count()

    return response

def update_color(obj):
    response = {}
    tag = m_Tag.objects.filter(id=obj['id_tag'])

    tag.update(color=obj['new_color'])
    response['status'] = 'success'

    return response

def update_name(obj, request):
    id_corpus = get_current_corpus(request)

    response = {}
    tag = m_Tag.objects.filter(id=obj['id_tag'])
    new_name = obj['new_name'].strip().replace(' ', '-')

    try:
        tag.update(name=new_name)
        response['status'] = 'success'
    except:
        print('non unique name')
        existing_tag = m_Tag.objects.get(name=new_name, key_corpus=id_corpus)
        response['status'] = 'error'
        response['data'] = {'id_tag': tag[0].id, 'id_tag_name': tag[0].name, 'existing_tag': existing_tag.id, 'existing_tag_name': existing_tag.name}

    return response
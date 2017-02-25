from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render


def tags(request):
    tags = m_Tag.objects.all()

    if request.method == 'POST':
        cookie_id = request.COOKIES['csrftoken']
        response = {}
        obj = json.loads(request.body.decode("utf-8"))

        if obj['task'] == 'set_session_entry':
            request.session['index__'+obj['session_key']] = obj['session_value']
            response['status'] = 'success'
        elif obj['task'] == 'update_name':
            response = update_name(obj)
        elif obj['task'] == 'merge_tags':
            response['data'] = merge_tags(obj)
        elif obj['task'] == 'update_color':
            response = update_color(obj)
        elif obj['task'] == 'delete_tag':
            response = delete_tag(obj)
        elif obj['task'] == 'export_tags':
            response = export_tags(obj)
        elif obj['task'] == 'import_tags':
            response = import_tags(obj)

        return JsonResponse(response)

    context = {}
    context['settings'] = DICT_SETTINGS_VIEWER
    context['tags'] = tags
    if request.is_ajax():
        return render(request, 'viewer/tags.html', context)
    else:
        return render(request, 'viewer/tags.html', context)

def import_tags(obj):
    response = {}

    if os.path.isfile(obj['path']):
        with open(obj['path'], 'r') as f:
            for line in f:
                obj_json = json.loads(line)

                obj_tag = m_Tag.objects.create(name = obj_json['name'], color = obj_json['color'])

                if DICT_SETTINGS_VIEWER['data_type'] == 'database':
                    ThroughModel = m_Tag.m2m_custom_model.through
                    list_tmp = []

                    for id_item in obj_json['ids']:
                        obj_db_entity = model_custom.objects.get(id_item=id_item)
                        list_tmp.append(ThroughModel(**{
                            'm_tag_id': obj_tag.pk, 
                            DICT_SETTINGS_VIEWER['model_name'].lower()+'_id': obj_db_entity.pk
                        }))
                        # list_tmp.append(ThroughModel(m_tag_id=obj_tag.pk, m_entity_id=obj_db_entity.pk))

                    ThroughModel.objects.bulk_create(list_tmp)
                else:
                    ThroughModel = m_Tag.m2m_entity.through
                    list_tmp = []

                    for id_item in obj_json['ids']:
                        obj_db_entity = m_Entity.objects.get(id_item=id_item)
                        list_tmp.append(ThroughModel(m_tag_id=obj_tag.pk, m_entity_id=obj_db_entity.pk))

                    ThroughModel.objects.bulk_create(list_tmp)

    return response

def export_tags(obj):
    response = {}

    if obj['path'].strip() != '':
        if not os.path.exists(obj['path']):
            os.makedirs(obj['path'])
        
    name_file = 'tags_exported_'+str(int(time.time()))+'.ldjson'
    path_file = os.path.join(obj['path'], name_file)


    with open(path_file, 'w') as f:
        queryset_tags = m_Tag.objects.all()
        if DICT_SETTINGS_VIEWER['data_type'] == 'database':
            queryset_tags = queryset_tags.prefetch_related('m2m_custom_model')
        else:
            queryset_tags = queryset_tags.prefetch_related('m2m_entity')
        for tag in queryset_tags:
            obj_tag = {}
            obj_tag['name'] = tag.name
            obj_tag['color'] = tag.color
            list_ids = []
            if DICT_SETTINGS_VIEWER['data_type'] == 'database':
                for entity in tag.m2m_custom_model.all():
                    list_ids.append(entity.id)
            else:
                for entity in tag.m2m_entity.all():
                    list_ids.append(entity.id_item)

            obj_tag['ids'] = list_ids
            f.write(json.dumps(obj_tag)+'\n')

    return response

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

def update_name(obj):
    response = {}
    tag = m_Tag.objects.filter(id=obj['id_tag'])
    new_name = obj['new_name'].strip().replace(' ', '-')

    try:
        tag.update(name=new_name)
        response['status'] = 'success'
    except:
        print('non unique name')
        existing_tag = m_Tag.objects.get(name=new_name)
        response['status'] = 'error'
        response['data'] = {'id_tag': tag[0].id, 'id_tag_name': tag[0].name, 'existing_tag': existing_tag.id, 'existing_tag_name': existing_tag.name}

    return response
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

        return JsonResponse(response)

    context = {}
    context['tags'] = tags
    if request.is_ajax():
        return render(request, 'viewer/tags.html', context)
    else:
        return render(request, 'viewer/tags.html', context)

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
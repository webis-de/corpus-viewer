from django.shortcuts import render, redirect
from viewer.views.shared_code import glob_manager_data, get_current_corpus
from viewer.models import m_Tag, m_Entity
import json
import os
from django.conf import settings
import urllib.request

def view_item(request, id_corpus, id_internal_item):
    # id_corpus = get_current_corpus(request)
    context = {}

    if glob_manager_data.has_corpus_secret_token(id_corpus):
        try:
            secret_token = request.session[id_corpus]['viewer__secret_token']
        except KeyError:
            secret_token = None
        if not glob_manager_data.is_secret_token_valid(id_corpus, secret_token):
            return redirect('viewer:add_token', id_corpus=id_corpus)  

    obj_item = glob_manager_data.get_item(id_corpus, int(id_internal_item))
    queryset_tags = m_Tag.objects.filter(m2m_entity__id_item_internal=id_internal_item, key_corpus=id_corpus)
    obj_item['viewer__tags'] = [{'name': tag.name, 'color': tag.color} for tag in queryset_tags]

    source_external = glob_manager_data.get_setting_for_corpus('external_source', id_corpus)

    if source_external != None:
        id_item = obj_item[glob_manager_data.get_setting_for_corpus('id', id_corpus)]
        url = source_external.replace('PLACEHOLDER_ID', str(id_item))
        if not url.startswith('http'):
            url = 'http://' + url
        print(url)

        with urllib.request.urlopen(url) as response:
            html = response.read().decode("utf8")
            context['template'] = html
    else:

        template_html = glob_manager_data.get_setting_for_corpus('template_html', id_corpus)
        if template_html == None:
            return redirect('viewer:index', id_corpus=id_corpus) 
        else:
            context['template'] = template_html

    context['json_item'] = json.dumps(obj_item)
    context['id_corpus'] = id_corpus
    context['name_corpus'] = glob_manager_data.get_setting_for_corpus('name', id_corpus)

    return render(request, 'viewer/view_item.html', context)
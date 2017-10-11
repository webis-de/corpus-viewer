from django.shortcuts import render, redirect
from viewer.views.shared_code import glob_manager_data, get_current_corpus
import json
import os
from django.conf import settings

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
    # print(id_corpus)
    # print(id_internal_item)
    obj_item = glob_manager_data.get_item(id_corpus, int(id_internal_item))
    # print(obj_item)
    # if request.method == 'POST':
    #     input_secret_token = request.POST.get('secret_token')
    #     request.session[id_corpus]['viewer__secret_token'] = input_secret_token
    #     request.session.modified = True
    #     return redirect('viewer:index')

    context['json_item'] = json.dumps(obj_item)
    context['id_corpus'] = id_corpus

    template_html = glob_manager_data.get_setting_for_corpus('template_html', id_corpus)
    if template_html == None:
        return redirect('viewer:index', id_corpus=id_corpus) 
    else:
        context['template'] = template_html

    return render(request, 'viewer/view_item.html', context)
from django.shortcuts import render, redirect
from viewer.views.shared_code import glob_manager_data, get_current_corpus
import json
import os
from django.conf import settings

def view_item(request, id_corpus, id_internal_item):
    # id_corpus = get_current_corpus(request)
    context = {}
    # print(id_corpus)
    # print(id_internal_item)
    obj_item = glob_manager_data.get_item(id_corpus, int(id_internal_item))
    # print(obj_item)
    # if request.method == 'POST':
    #     input_secret_token = request.POST.get('secret_token')
    #     request.session[id_corpus]['viewer__secret_token'] = input_secret_token
    #     request.session.modified = True
    #     return redirect('viewer:index')
    link_template = os.path.join(glob_manager_data.path_templates, id_corpus+'.html')

    if not os.path.isfile(link_template):
        return redirect('viewer:index', id_corpus=id_corpus) 

    context['json_item'] = json.dumps(obj_item)
    context['id_corpus'] = id_corpus
    with open(glob_manager_data.get_setting_for_corpus('template', id_corpus), 'r') as f:
        context['template'] = f.read()
    # context['link_template'] = link_template
    return render(request, 'viewer/view_item.html', context)
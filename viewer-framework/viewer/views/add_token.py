from django.shortcuts import render, redirect
from .shared_code import glob_manager_data
import os 

def add_token(request, id_corpus):
    context = {}

    if request.method == 'POST':
        input_secret_token = request.POST.get('secret_token')
        request.session[id_corpus]['viewer__secret_token'] = input_secret_token
        request.session.modified = True
        return redirect('viewer:index', id_corpus=id_corpus)

    context['secret_token_help'] = glob_manager_data.get_setting_for_corpus('secret_token_help', id_corpus)
    return render(request, 'viewer/add_token.html', context)
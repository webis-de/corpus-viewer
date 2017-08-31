from django.shortcuts import render, redirect
import os 

def add_token(request, id_corpus):
    context = {}

    if request.method == 'POST':
        input_secret_token = request.POST.get('secret_token')
        request.session[id_corpus]['viewer__secret_token'] = input_secret_token
        request.session.modified = True
        return redirect('viewer:index')

    return render(request, 'viewer/add_token.html', context)
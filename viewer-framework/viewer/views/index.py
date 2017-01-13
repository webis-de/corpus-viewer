from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render

def index(request):
    # request.session.flush()
##### handle session entries
    set_session(request, 'is_collapsed_div_filters', True)
    set_session_from_url(request, 'filter_text_content', 'ewrwfd')

    print(request.session['viewer__filter_text_content'])
##### apply filters

##### handle post requests
    print(DICT_SETTINGS_VIEWER)
    context = {}
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)

def tags(request):
    context = {}
    return render(request, 'viewer/tags.html', context)

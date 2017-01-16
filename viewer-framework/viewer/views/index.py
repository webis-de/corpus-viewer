from .shared_code import *
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    # index_example_data()
    # request.session.flush()
##### handle post requests
    # print(DICT_SETTINGS_VIEWER)
    
    context = {}
    context['settings'] = DICT_SETTINGS_VIEWER
    return render(request, 'viewer/index.html', context)

def tags(request):
    context = {}
    return render(request, 'viewer/tags.html', context)
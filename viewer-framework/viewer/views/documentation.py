# from .shared_code import get_setting, set_sessions, get_current_corpus
from django.shortcuts import render


def documentation(request):
    context = {}
    context['url_host'] = 'http://webis24.medien.uni-weimar.de:8080'
    context['name_host'] = 'webis24'
    return render(request, 'viewer/documentation.html', context)
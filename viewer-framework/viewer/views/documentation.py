from django.shortcuts import render
import os 

def documentation(request):
    context = {}

    with open(os.path.join('..', 'settings', 'settings_viewer_example.py')) as f:
        context['example_setting_file'] = f.read()

    context['url_host'] = 'http://webis24.medien.uni-weimar.de:8080'
    context['name_host'] = 'webis24'
    return render(request, 'viewer/documentation.html', context)
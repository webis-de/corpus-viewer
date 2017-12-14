from .shared_code import get_current_corpus, glob_manager_data
from django.http import JsonResponse
from django.shortcuts import render, redirect

def edit(request, id_corpus):
    # with open('int.bin', 'w') as f:
    #     for x in range(0, 20 * 100 000 000):
    #             f.write(1)

    if not glob_manager_data.get_has_access_to_editing(id_corpus, request):
        return redirect('viewer:index', id_corpus=id_corpus) 

    if request.method == 'POST':
        cookie_id = request.COOKIES['csrftoken']

        content = request.POST['content']
        glob_manager_data.set_settings_content_for_corpus(id_corpus, content)
        if glob_manager_data.reload_settings(id_corpus) == None:
                print('ERROR')
        else:
            return redirect('viewer:index', id_corpus)

    context = {}
    context['content_settings'] = glob_manager_data.get_settings_content_for_corpus(id_corpus)
    context['id_corpus'] = id_corpus
    context['name_corpus'] = glob_manager_data.get_setting_for_corpus('name', id_corpus)
    context['mode_navbar'] = 'viewer'
    return render(request, 'viewer/edit.html', context)

from .shared_code import get_current_corpus, glob_manager_data
from django.http import JsonResponse
import json

def api_refresh_corpora(request):
    dict_result = {}
    
    glob_manager_data.check_for_new_corpora()

    dict_result['success'] = True
    return JsonResponse(dict_result)


def api_add_corpus(request):
    dict_result = {}

    print(request.POST)

    glob_manager_data.add_settings_corpus(request.POST['id_corpus'], json.loads(request.POST['settings']))

    dict_result['success'] = True
    return JsonResponse(dict_result)


def api_delete_corpus(request):
    dict_result = {}

    print(request.POST)
    glob_manager_data.delete_corpus(request.POST['id_corpus'], False)
    # glob_manager_data.add_settings_corpus(request.POST['id_corpus'], json.loads(request.POST['settings']))

    dict_result['success'] = True
    return JsonResponse(dict_result)

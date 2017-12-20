from .shared_code import get_current_corpus, glob_manager_data
from django.http import JsonResponse

def api_refresh_corpora(request):
    dict_result = {}
    
    glob_manager_data.check_for_new_corpora()

    dict_result['success'] = True
    return JsonResponse(dict_result)

from settings_viewer import DICT_SETTINGS_VIEWER

def set_session(request, key, default):
    sessionkey = 'viewer__'+key
    if sessionkey not in request.session:
        request.session[sessionkey] = default

def set_session_from_url(request, key, default):
    print(key, default)
    sessionkey = 'viewer__'+key
    if request.GET.get(key) != None:
        request.session[sessionkey] = request.GET.get(key)
    else:
        if sessionkey not in request.session:
            request.session[sessionkey] = default

import time
import json
import csv
from settings_viewer import DICT_SETTINGS_VIEWER
from viewer.models import m_Tag, m_Entity, Example_Model

def index_example_data():
    list_entries = []
    for i in range(1000):
        list_entries.append(Example_Model(name='name'+str(i), count_of_something=i))

    Example_Model.objects.bulk_create(list_entries)

def set_session(request, key, default):
    sessionkey = 'viewer__'+key
    if sessionkey not in request.session:
        request.session[sessionkey] = default

def set_session_from_url(request, key, default):
    sessionkey = 'viewer__'+key

    if request.GET.get(key) != None:
        request.session[sessionkey] = request.GET.get(key)
    else:
        if sessionkey not in request.session:
            request.session[sessionkey] = default

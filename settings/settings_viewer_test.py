import os
import csv
import json

def load_data(item_handle):
    print('function 2')

    # for x in range(0,10):
    #     obj = {}
    #     obj['id'] = x
    #     obj['text'] = 'this is only a test test'

    item_handle.add({'id':0, 'text': 'test'})
    item_handle.add({'id':1, 'text': 'test test abc'})
    item_handle.add({'id':2, 'text': 'Test test '})
    item_handle.add({'id':5, 'text': 'abc test test'})
    item_handle.add({'id':3, 'text': 'TESTTEST'})
    item_handle.add({'id':4, 'text': ''})


DICT_SETTINGS_VIEWER = {
    # possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
    'name': 'test',
    'description': '',
    'data_type': 'custom',
        # only necessary if data_type is '*-file'
            # path to data,
            # 'data_path': '../corpora/webis-cbc-16',
            'data_path': '../corpora/file.ldjson',
            # structure of data in file
            'data_structure': ['name', 'retweet_count', 'id'],


        # only necessary if data_type is 'custom'
            # function to load the data
            'load_data_function': load_data,
        # only necessary if data_type is 'database'
            # name of the app where the model is located
            'app_label': 'example_app',
            # name of the model
            'model_name': 'Example_Model',
    'use_cache': True,
    'data_fields': {
        'id': {
            'type': 'number',
            'display_name': 'ID'
        },
        'text': {
            'type': 'string',
            'display_name': 'Text'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'text'
    ],
    'page_size': 10,
    # Possible filter types: 'text', 'checkbox'
    #
    'filters': [
        {
            'data_field': 'text',
            'description': 'Text',
            'placeholder': 'Text Input',
            'default_value': '',
        },
        {
            'data_field': 'id',
            'description': 'Id',
            'placeholder': 'Count Input',
            'default_value': '',
        },
    ],
    # 'secret_token': 'test',
    'external_source': None,
    # 'template': '../corpora/template_query_speller.html',
}
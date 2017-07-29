import os
import csv
import json

def load_data(item_handle):
    for x in range(0, 100):
        obj = {}
        obj['id'] = x
        obj['string'] = 'Test string of item ' + str(x)
        obj['text'] = 'This is only a longer test text of item ' + str(x) + ' to show the behaviour of long texts in the corpus viewer.'
        item_handle.add(obj)

DICT_SETTINGS_VIEWER = {
    # possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
    'name': 'Example',
    'description': 'This is an example corpus.',
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
            'type': 'text',
            'display_name': 'Text'
        },
        'string': {
            'type': 'string',
            'display_name': 'String'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'text', 'string'
    ],
    'page_size': 25,
    'filters': [
        {
            'data_field': 'text',
            'description': 'Text',
            'placeholder': 'Text Input',
            'default_value': '',
        },
        {
            'data_field': 'string',
            'description': 'String',
            'placeholder': 'String Input',
            'default_value': '',
        },
        {
            'data_field': 'id',
            'description': 'Id',
            'placeholder': 'Count Input',
            'default_value': '',
        },
    ],
}
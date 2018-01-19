import os
import csv
import json

def load_data(item_handle):
    text = '2132'
    # text = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'

    # with open('../large_corpus.txt') as f:
    #     counter = 0
    #     for line in f:
    #         obj = {}
    #         obj['id'] = counter
    #         obj['text'] = text  
    #         item_handle.add(obj)
    #         counter += 1
    #         if counter % 1000000 == 0:
    #             print(counter)
    #         if counter == 10000000:
    #             return

    # for x in range(0, 1):
    for x in range(0, 1000000):
    # for x in range(0, 100000):
    # for x in range(0, 1000000):
    # for x in range(0, 5000000):
        obj = {}
        obj['id'] = 'id_'+str(x)
        obj['text'] = text
        # obj['text'] = 'text_'+str(x % 5)
        item_handle.add(obj)



DICT_SETTINGS_VIEWER = {
    # possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
    'name': 'large corpus',
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
            'type': 'string',
            'display_name': 'ID'
        },
        'text': {
            # 'type': 'string',
            'type': 'text',
            'display_name': 'Text'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'text'
    ],
    'secret_token_editing': '',
    'page_size': 25,
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
}
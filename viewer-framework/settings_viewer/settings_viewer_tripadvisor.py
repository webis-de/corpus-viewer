import os
import xmltodict
import json

def load_data():
    data = []
    
    path_corpus = '../corpora/corpus-arguana-tripadvisor/uima/uima/annotated-by-experts'
    path_data = os.path.join(path_corpus, 'test')

    counter_id = 0
    for city in os.listdir(path_data):
        path_city = os.path.join(path_data, city)
        if len(city) > 30:
            continue
        for annotation in os.listdir(path_city):
            if annotation.endswith('DS_Store') or len(annotation) > 30:
                continue

            with open(os.path.join(path_city, annotation), 'r') as f:
                dict_obj = xmltodict.parse(f.read())
                obj_data = {}

                obj_data['id'] = counter_id
                counter_id += 1
                obj_data['city'] = city
                obj_data['text'] = dict_obj['xmi:XMI']['cas:Sofa']['@sofaString']
                obj_data['author'] = dict_obj['xmi:XMI']['arguana:RatingData']['@author']
                try:
                    obj_data['location'] = float(dict_obj['xmi:XMI']['arguana:Aspects']['@location'])
                except:
                    obj_data['location'] = -1

                data.append(obj_data)

    return data

def load_annotations(path_truth, annotator):
    dict_annotations = {}
    with open(os.path.join(path_truth, annotator+'.csv'), 'r') as f:
        spamreader = csv.reader(f)
        for row in spamreader:
            id_tweet = int(row[0])
            score = row[1]
            dict_annotations[id_tweet] = score

    return dict_annotations

DICT_SETTINGS_VIEWER = {
    # possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
    'name': 'tripadvisor',
    'description': 'Description of the tripadvisor corpus',
    'data_type': 'custom',
        # only necessary if data_type is '*-file' or 'custom'
            # path to data,
            # 'data_path': '../corpora/webis-cbc-16',
            'data_path': '../corpora/file.ldjson',
            # structure of data in file
            'data_structure': ['text', 'retweet_count', 'id'],


        # only necessary if data_type is 'custom'
            # function to load the data
            'load_data_function': load_data,
        # only necessary if data_type is 'database'
            # name of the app where the model is located
            'app_label': 'example_app',
            # name of the model
            'model_name': 'Example_Model',
    'use_cache': False,
    'data_fields': {
        'id': {
            'type': 'int',
            'display_name': 'ID'
        },
        'city': {
            'type': 'string',
            'display_name': 'City'
        },
        'text': {
            'type': 'text',
            'display_name': 'Text'
        },
        'author': {
            'type': 'text',
            'display_name': 'Author'
        },
        'location': {
            'type': 'int',
            'display_name': 'Location'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'city', 'text', 'author', 'location'
    ],
    'page_size': 25,
    # Possible filter types: 'text', 'checkbox'
    #
    'filters': [
        # {
        #   'type': 'checkbox',
        #   'data_field_name': 'retweet_count',
        #   'description': 'Some Checkbox',
        #   'default_value': False,
        #   'event': 'change'
        # },
        {
            'type': 'contains',
            'data_field': 'city',
            'description': 'City',
            'placeholder': 'Text Input',
            'default_value': '',
            'event': 'change'
        },
        {
            'type': 'contains',
            'data_field': 'text',
            'description': 'Text',
            'placeholder': 'Text Input',
            'default_value': '',
            'event': 'change'
        },
        {
            'type': 'number',
            'data_field': 'location',
            'description': 'Location Rating',
            'placeholder': 'Text Input',
            'default_value': '',
            'event': 'change'
        },
    ],
}
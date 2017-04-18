import os
import csv
import json

def load_data():
    data = []
    
    path_corpora = '../corpora/webis-cbc-16'
    path_truth = os.path.join(path_corpora, 'truth')
    path_problems = os.path.join(path_corpora, 'problems')


    dict_annotations_annotatorA = load_annotations(path_truth, 'annotatorA')
    dict_annotations_annotatorB = load_annotations(path_truth, 'annotatorB')
    dict_annotations_annotatorC = load_annotations(path_truth, 'annotatorC')
    dict_annotations_majority = load_annotations(path_truth, 'majority')

    counter_error = 0
    for folder in os.listdir(path_problems):
        path_problem = os.path.join(path_problems, folder)
        for file in os.listdir(path_problem):
            path_file = os.path.join(path_problem, file)
            if file.endswith('.json'):
                with open(path_file, 'r') as f:
                    try:
                        obj_json = json.loads(f.read())
                        obj_tweet = {}
                        obj_tweet['id'] = obj_json['id']
                        obj_tweet['text'] = obj_json['text']
                        obj_tweet['retweet_count'] = obj_json['retweet_count']
                        obj_tweet['annotatorA'] = dict_annotations_annotatorA[obj_json['id']]
                        obj_tweet['annotatorB'] = dict_annotations_annotatorB[obj_json['id']]
                        obj_tweet['annotatorC'] = dict_annotations_annotatorC[obj_json['id']]
                        obj_tweet['majority'] = dict_annotations_majority[obj_json['id']]
                        data.append(obj_tweet)
                    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
                        counter_error += 1

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
    'data_type': 'custom',
        # only necessary if data_type is '*-file' or 'custom'
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
            'type': 'int',
            'display_name': 'ID'
        },
        'text': {
            'type': 'string',
            'display_name': 'Text'
        },
        'retweet_count': {
            'type': 'int',
            'display_name': 'Retweets'
        },
        'annotatorA': {
            'type': 'string',
            'display_name': 'A'
        },
        'annotatorB': {
            'type': 'string',
            'display_name': 'B'
        },
        'annotatorC': {
            'type': 'string',
            'display_name': 'C'
        },
        'majority': {
            'type': 'string',
            'display_name': 'majority'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'retweet_count', 'text', 'annotatorA', 'annotatorB', 'annotatorC', 'majority'
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
            'data_field': 'text',
            'description': 'Tweet Text',
            'placeholder': 'Text Input',
            'default_value': '',
            'event': 'change'
        },
        {
            'type': 'number',
            'data_field': 'retweet_count',
            'description': 'Count Retweets',
            'placeholder': 'Count Input',
            'default_value': '',
            'event': 'change'
        },
    ],
}
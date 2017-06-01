import os
import xmltodict
import json

def load_data():
    data = []
    
    path_corpus = '../corpora/dagstuhl-15512-argquality-corpus'
    path_data = os.path.join(path_corpus, 'dagstuhl-15512-argquality-corpus-annotated-xmi')

    counter_id = 0
    for topic in os.listdir(path_data):
        path_topic = os.path.join(path_data, topic)
        if len(topic) > 30:
            continue
        for opinion in os.listdir(path_topic):
            if opinion.endswith('DS_Store') or len(opinion) > 30:
                continue
            path_opinion = os.path.join(path_topic, opinion)
            for annotation in os.listdir(path_opinion):
                if annotation.endswith('DS_Store') or len(annotation) > 30:
                    continue

                with open(os.path.join(path_opinion, annotation), 'r') as f:
                    dict_obj = xmltodict.parse(f.read())
                    obj_data = {}

                    obj_data['id'] = counter_id
                    counter_id += 1
                    obj_data['topic'] = topic
                    obj_data['opinion'] = opinion
                    obj_data['text'] = dict_obj['xmi:XMI']['cas:Sofa']['@sofaString']

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
    'name': 'arg',
    'description': 'Description of the argumentation corpus',
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
        'topic': {
            'type': 'string',
            'display_name': 'Topic'
        },
        'opinion': {
            'type': 'string',
            'display_name': 'Opinion'
        },
        'text': {
            'type': 'string',
            'display_name': 'Text'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'topic', 'opinion', 'text'
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
            'data_field': 'topic',
            'description': 'Topic',
            'placeholder': 'Text Input',
            'default_value': '',
            'event': 'change'
        },
        {
            'type': 'contains',
            'data_field': 'opinion',
            'description': 'Opinion',
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
    ],
}
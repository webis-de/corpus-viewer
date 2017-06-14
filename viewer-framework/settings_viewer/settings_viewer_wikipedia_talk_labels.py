import os
import csv
import json

def load_data():
    # This is the final list. 
    # Each list item contains one entity of your corpus, represented as a python dictionary.
    data = []
    
    # Relative path to the corpus (currently its simply on webis24) 
    path_corpus = '../corpora/wikipedia_talk_labels'
    file_comments = os.path.join(path_corpus, 'attack_annotated_comments.tsv')
    file_annotations = os.path.join(path_corpus, 'attack_annotations.tsv')
    file_worker_demographics = os.path.join(path_corpus, 'attack_worker_demographics.tsv')

    # load the data from the worker-demographics-file and store it as a dictionary with the worker-ids as keys
    dict_worker_demographics = load_worker_demographics(file_worker_demographics)
    # load the data from the annotations-file and store it as a dictionary with the comment-ids as keys
    # append the corresponding worker information to each annotation 
    dict_annotations = load_annotations(file_annotations, dict_worker_demographics)

    
    with open(file_comments, 'r') as f:
        reader_tsv = csv.reader(f, delimiter='\t')
        for index, row in enumerate(reader_tsv):
            # skip the first line of the file (header)
            if index == 0:
                continue

            rev_id = int(row[0])
            string_comment = row[1]
            year = int(row[2])
            logged_in = bool(row[3])
            ns = row[4]
            sample = row[5]
            split = row[6]

            comment = {}
            comment['rev_id'] = rev_id
            comment['comment'] = string_comment
            comment['year'] = year
            comment['logged_in'] = logged_in
            comment['ns'] = ns
            comment['sample'] = sample
            comment['split'] = split
            comment['attack'] = ', '.join([str(value['attack']) for value in dict_annotations[rev_id]])
            comment['annotations'] = dict_annotations[rev_id]
            comment['number_of_annotations'] = len(dict_annotations[rev_id])

            data.append(comment)

    return data

def load_worker_demographics(file_worker_demographics):
    dict_worker_demographics = {}
    
    with open(file_worker_demographics, 'r') as f:
        reader_tsv = csv.reader(f, delimiter='\t')
        for index, row in enumerate(reader_tsv):
            # skip the first line of the file (header)
            if index == 0:
                continue

            worker_id = int(row[0])
            gender = row[1]
            english_first_language = False if row[2] == 0 else True
            age_group = row[3]
            education = row[4]

            worker_demographic = {}
            worker_demographic['id'] = worker_id
            worker_demographic['gender'] = gender
            worker_demographic['english_first_language'] = english_first_language
            worker_demographic['age_group'] = age_group
            worker_demographic['education'] = education

            dict_worker_demographics[worker_id] = worker_demographic

    return dict_worker_demographics

def load_annotations(file_annotations, dict_worker_demographics):
    dict_annotations = {}
    errors = 0
    set_workers = set()

    with open(file_annotations, 'r') as f:
        reader_tsv = csv.reader(f, delimiter='\t')
        for index, row in enumerate(reader_tsv):
            # skip the first line of the file (header)
            if index == 0:
                continue
            rev_id = int(row[0])
            worker_id = int(row[1])
            quoting_attack = float(row[2])
            recipient_attack = float(row[3])
            third_party_attack = float(row[4])
            other_attack = float(row[5])
            attack = float(row[6])

            if not rev_id in dict_annotations:
                dict_annotations[rev_id] = []

            annotation = {}
            annotation['rev_id'] = rev_id
            try:
                annotation['worker'] = dict_worker_demographics[worker_id]
            except KeyError:
                annotation['worker'] = {'id': worker_id}
                set_workers.add(worker_id)
                errors += 1
            annotation['quoting_attack'] = quoting_attack
            annotation['recipient_attack'] = recipient_attack
            annotation['third_party_attack'] = third_party_attack
            annotation['other_attack'] = other_attack
            annotation['attack'] = attack

            dict_annotations[rev_id].append(annotation)

    print('annotations without workers: '+str(errors))
    print('number of unrecognized workers: '+str(len(set_workers)))

    return dict_annotations

DICT_SETTINGS_VIEWER = {
    'name': 'Wikipedia Talk Label',
    'description': 'Description of this corpus.<br><a href="https://figshare.com/articles/Wikipedia_Talk_Labels_Personal_Attacks/4054689">Link</a> to page.',
    # specify the input format
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
    # enable/disable the caching functionality
    'use_cache': True,
    # which data-fields (columns) of the input data should be registered to the viewer?
    'data_fields': {
        'rev_id': {
            'type': 'int',
            'display_name': 'ID'
        },
        'comment': {
            'type': 'text',
            'display_name': 'Comment'
        },
        'year': {
            'type': 'int',
            'display_name': 'Year'
        },
        'logged_in': {
            'type': 'bool',
            'display_name': 'Logged in'
        },
        'ns': {
            'type': 'string',
            'display_name': 'ns'
        },
        'sample': {
            'type': 'string',
            'display_name': 'Sample'
        },
        'split': {
            'type': 'string',
            'display_name': 'Split'
        },
        'number_of_annotations': {
            'type': 'int',
            'display_name': '#Annotations'
        },
        'attack': {
            'type': 'string',
            'display_name': 'attack'
        }
    },
    # which of the data-fields is the key?
    'id': 'rev_id',
    # which of the data_fields should be displayed in the viewer?
    'displayed_fields': [
        'rev_id', 'comment', 'year', 'logged_in', 'ns', 'sample', 'split', 'number_of_annotations','attack'
    ],
    # number of items (rows) for each page
    'page_size': 25,
    # specify the filters for the viewer
    'filters': [
        {
            'type': 'contains',
            'data_field': 'split',
            'description': 'Split',
            'placeholder': 'Text Input',
            'default_value': '',
            'event': 'change'
        },
        {
            'type': 'number',
            'data_field': 'year',
            'description': 'Year',
            'placeholder': 'Year',
            'default_value': '',
            'event': 'change'
        },
        {
            'type': 'number',
            'data_field': 'number_of_annotations',
            'description': 'Number of annotations',
            'placeholder': 'Number of annotations',
            'default_value': '',
            'event': 'change'
        },
	{
            'type': 'contains',
            'data_field': 'comment',
            'description': 'comment',
            'placeholder': 'Text Input',
            'default_value': '',
            'event': 'change'
        },
    ],
}
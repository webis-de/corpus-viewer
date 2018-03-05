def load_data(item_handle):
    import os
    import json

    path_file_users = '/data_corpus/example_data.ldjson'

    with open(path_file_users, 'r') as f:
        for index, line in enumerate(f):
            item_handle.add(json.loads(line))

# this is the main dictionary containing the necessary information to load and display your corpus
DICT_SETTINGS_VIEWER = {
    'id_corpus': 'netspeak',
    'name': '3. Netspeak',
    'description': 'This corpus contains the query logs from <a href="http://www.netspeak.org/" target="_blank">Netspeak</a>',
    'data_type': 'custom',
    'load_data_function': load_data,
    'data_fields': {
        'id': {
            'type': 'number',
            'display_name': 'ID'
        },
        'ip': {
            'type': 'string',
            'display_name': 'IP'
        },
        'count_interactions_v1_2': {
            'type': 'number',
            'display_name': 'Pre-Instant'
        },
        'count_interactions_v3': {
            'type': 'number',
            'display_name': 'Instant'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'ip', 'count_interactions_v1_2', 'count_interactions_v3'
    ],
    'page_size': 25,
    'filters': [
        {
            'data_field': 'id',
            'description': 'ID',
            'placeholder': 'ID',
            'default_value': '',
        },
        {
            'data_field': 'ip',
            'description': 'IP',
            'placeholder': 'IP',
            'default_value': '',
        },
        # {
        #     'data_field': 'majority',
        #     'description': 'Majority',
        #     'placeholder': 'Text Input',
        #     'default_value': '',
        # },
        # {
        #     'data_field': 'retweet_count',
        #     'description': 'Count Retweets',
        #     'placeholder': 'Count Input',
        #     'default_value': '',
        # },
    ],
    'external_source': 'http://webis24.medien.uni-weimar.de:8001/browser/stream/PLACEHOLDER_ID',
    # 'secret_token': 'test',
    'secret_token_editing': '',
    # 'template_path': '../corpora/webis-cbc-16/template.html'
}

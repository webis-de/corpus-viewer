# this is the main dictionary containing the necessary information to load and display your corpus
DICT_SETTINGS_VIEWER = {
    'name': 'Database',
    'description': '',
    'data_type': 'database',
    'app_label': 'example_app',
    'model_name': 'Example_Model',
    'database_prefetch_related': [
    ],
    'database_select_related': [
    ],
    'database_filters': {
    },

    'data_fields': {
        'id': {
            'type': 'number',
            'display_name': 'ID'
        },
        'name': {
            'type': 'string',
            'display_name': 'Name'
        },
        'count_of_something': {
            'type': 'number',
            'display_name': 'Count'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'name', 'count_of_something'
    ],
    'page_size': 25,
    'filters': [
        {
            'data_field': 'count_of_something',
            'description': 'Count',
            'placeholder': '',
        },
    ],
    'secret_token_editing': '',
    # 'secret_token': 'test',
    # 'secret_token_editing': 'tesst',
    # 'template': '../corpora/index.html'
}

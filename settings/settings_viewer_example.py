def load_data(item_handle):
    # put import statements inside of this function: 
    # import o
    import random
    # import json
    # import csv

    # create some example items for the corpus
    for x in range(0, 100):
        obj = {}
        obj['id'] = x
        obj['some_boolean_value'] = random.choice([True, False])
        obj['some_short_text'] = 'Test string of item ' + str(x)
        obj['some_longer_text'] = 'This is only a longer test text of item ' + str(x) + ' to show the behaviour of long texts in the corpus viewer.'
        # register the item to the viewer
        item_handle.add(obj)

# this is the main dictionary containing the necessary information to load and display your corpus
DICT_SETTINGS_VIEWER = {
    'name': 'Example',
    'description': 'This is an example corpus which is password protected. The password is \'test\'',
    'data_type': 'custom',
    'load_data_function': load_data,

    # the following two items are used only if 'data_type' is set to ldjson or csv 
    'data_path': '../corpora/file.ldjson',
    'data_structure': ['id', 'some_short_text', 'some_longer_text'],

    'data_fields': {
        'id': {
            'type': 'number',
            'display_name': 'ID'
        },
        'some_boolean_value': {
            'type': 'boolean',
            'display_name': 'Boolean'
        },
        'some_short_text': {
            'type': 'string',
            'display_name': 'Text'
        },
        'some_longer_text': {
            'type': 'text',
            'display_name': 'String'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'some_boolean_value', 'some_short_text', 'some_longer_text'
    ],
    'page_size': 25,
    'filters': [
        {
            'data_field': 'some_longer_text',
            'description': 'Text',
            'placeholder': 'Text input',
            'default_value': '',
        },
        {
            'data_field': 'some_boolean_value',
            'description': 'Bool',
            'placeholder': 'Text input',
            'default_value': '',
        },
        {
            'data_field': 'some_short_text',
            'description': 'String',
            'placeholder': 'String input',
            'default_value': '',
        },
        {
            'data_field': 'id',
            'description': 'Id',
            'placeholder': 'Count input',
            'default_value': '',
        },
    ],
    'secret_token': 'test',
    'secret_token_editing': '',
    'template': '../corpora/index.html',
    'secret_token_help': None,
}

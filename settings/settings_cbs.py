def load_data(item_handle):
    import pandas as pd
    import numpy as np

    df = pd.read_pickle('../clickbait-corpus-3.p')
    headers = df.columns

    for idx, row in df.iterrows():
        obj = {}
        for col in headers:
            obj[col] = row[col]
        
        item_handle.add(obj)

DICT_SETTINGS_VIEWER = {
    # possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
    'name': 'Clickbait Spoiling',
    'description': 'Spoiler Corpus',
    'data_type': 'ldjson-file',
        # only necessary if data_type is '*-file'
            # path to data,
            # 'data_path': '../corpora/webis-cbc-16',
            'data_path': '../clickbait-corpus-3.ldjson',
            # structure of data in file
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
        'post_id_str': {
            'type': 'string',
            'display_name': 'ID'
        },
        'cb_spoilers': {
            'type': 'string',
            'display_name': 'Spoiler'
        },
        'answer_type': {
            'type': 'string',
            'display_name': 'Answer Type'
        },
        # 'article_description': {
        #     'type': 'string',
        #     'display_name': 'article_description'
        # },
        # 'article_imgs': {
        #     'type': 'list',
        #     'display_name': 'article_imgs'
        # },
        # 'article_keywords': {
        #     'type': 'list',
        #     'display_name': 'article_keywords'
        # },
        # 'article_movies': {
        #     'type': 'list',
        #     'display_name': 'article_movies'
        # },
        # 'article_tags': {
        #     'type': 'list',
        #     'display_name': 'article_tags'
        # },
        # 'article_text': {
        #     'type': 'text',
        #     'display_name': 'article_text',
        # },
        # 'article_title': {
        #     'type': 'text',
        #     'display_name': 'article_title'
        # },
        # 'article_url': {
        #     'type': 'string',
        #     'display_name': 'article_url'
        # },
        # 'categories': {
        #     'type': 'list',
        #     'display_name': 'categories'
        # },
        # 'cb_headline': {
        #     'type': 'string',
        #     'display_name': 'cb_headline'
        # },
        # 'modified_spoiler': {
        #     'type': 'list',
        #     'display_name': 'modified_spoiler'
        # },
        # 'social_media_platform': {
        #     'type': 'string',
        #     'display_name': 'social_media_platform'
        # },
        # 'spoiler_named_entities': {
        #     'type': 'list',
        #     'display_name': 'spoiler_named_entities'
        # },
        # 'spoiler_publisher': {
        #     'type': 'string',
        #     'display_name': 'spoiler_publisher'
        # },
        # 'spoiler_word': {
        #     'type': 'list',
        #     'display_name': 'spoiler_word'
        # }
        
    },
    'id': 'post_id_str',
    'displayed_fields': [
        'post_id_str', 'cb_spoiler', 'answer_type'
    ],
    'page_size': 25,
    'filters': [
    ],
    # 'secret_token': 'test'
}

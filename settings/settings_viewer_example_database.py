DICT_SETTINGS_VIEWER = {
    'name': 'Database Example',
    'description': 'This corpus gets its data from a database',
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
        'some_boolean_value': {
            'type': 'boolean',
            'display_name': 'Boolean'
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
        'id', 'name', 'count_of_something', 'some_boolean_value'
    ],
    'page_size': 25,
    'filters': [
        {
            'data_field': 'count_of_something',
            'description': 'Count',
            'placeholder': '',
        },
        {
            'data_field': 'some_boolean_value',
            'description': 'Boolean',
            'placeholder': 'Text input',
            'default_value': '',
        },
    ],
    'secret_token_editing': '',
    'cards': [
        {
            'name': 'Load dummy data',
            'content': '''
                <div class="mb-2">
                    Press the button below to load the dummy data
                </div>
                <div class="">
                    <button type="button" id="button_index_dummy_data" class="btn btn-sm btn-primary">Load</button>
                </div>
                <script>
                    $(document).ready(function()
                    {
                        $(document).on('click', '#button_index_dummy_data', function(e) {
                            $.ajax({
                                url: '/example_app',
                                contentType: 'application/json',
                                success: function(result) { 
                                    load_current_page();
                                }
                            })
                        });

                    });
                </script>
            '''
        }
    ],
    # 'secret_token': 'test',
    # 'secret_token': 'test',
    'secret_token_editing': '',
    # 'template': '../corpora/index.html'
}

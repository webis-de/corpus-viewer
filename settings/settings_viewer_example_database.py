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
    'cards': [
        {
            'name': 'Index dummy data',
            'content': '''
                <div class="mb-2">
                    Press the button below to index the dummy data
                </div>
                <div class="">
                    <button type="button" id="button_index_dummy_data" class="btn btn-sm btn-primary">Approve</button>
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
    # 'secret_token_editing': 'tesst',
    # 'template': '../corpora/index.html'
}

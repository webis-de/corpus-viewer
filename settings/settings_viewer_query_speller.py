def load_data(item_handle):
    import csv
    
    def get_corrections(row):
        list_corrections = []
        for element in row[2:]:
            if element == '':
                break
            else: 
                list_corrections.append(element)
        return list_corrections

    path = "../corpora/webis-query-speller-corpus.csv"
    with open(path, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in spamreader:
            list_corrections = get_corrections(row)

            entry = {}
            entry['id'] = row[0]
            entry['query'] = row[1]
            entry['corrections'] = ', '.join(list_corrections)
            entry['count_corrections'] = len(list_corrections)

            item_handle.add(entry)


DICT_SETTINGS_VIEWER = {
    # possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
    'name': 'Webis-QSpell-17',
    'description': '',
    'data_type': 'custom',
    # function to load the data
    'load_data_function': load_data,
    'use_cache': True,
    'data_fields': {
        'id': {
            'type': 'number',
            'display_name': 'ID'
        },
        'corrections': {
            'type': 'text',
            'display_name': 'Spelling variants'
        },
        'query': {
            'type': 'string',
            'display_name': 'Query'
        },
        'count_corrections': {
            'type': 'number',
            'display_name': '#Variants'
        }
    },
    'id': 'id',
    'displayed_fields': [
        'id', 'query', 'count_corrections', 'corrections'
    ],
    'page_size': 25,
    'filters': [
        {
            'data_field': 'query',
            'description': 'Query',
            'placeholder': '',
            'default_value': '',
        },
        {
            'data_field': 'id',
            'description': 'ID',
            'placeholder': '',
            'default_value': '',
        },
        {
            'data_field': 'count_corrections',
            'description': '#Variants',
            'placeholder': '',
            'default_value': '',
        },
        {
            'data_field': 'corrections',
            'description': 'Variants',
            'placeholder': '',
            'default_value': '',
        },
    ],
    'secret_token_tagging': '1234',
    'template_html': """<dom-module id="viewer-template">

    <template>
        <link rel="stylesheet" href="[[ bootstrapCss ]]">
        <style>
            /* shadow DOM styles go here */
            :host {
                /*display: inline-block;*/
            }

        </style>
        <div class="row">
            <div class="col">
                <h1>Query: "{{ objItem.query }}"</h1>

                <table id="table_test" class="table table-striped">
                    <thead>
                        <tr>
                            <th></th>
                            <th>Variants</th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        </div>
    </template>

    <script>
        function get_position_of_first_difference(a, b) {
            let length_a = a.length;
            let length_b = b.length;

            let position = -1;

            for (let i = 0; i < a.length; i++) 
            {
                character_current_a = a[i];
                if(i < length_b)
                {
                    character_current_b = b[i];
                    if(character_current_a != character_current_b)
                    {
                        return i
                    }
                } else {
                    return position;
                }
            }
            return position;
        }

        class ViewerTemplate extends Polymer.Element {
            static get is() {
                return 'viewer-template';
            }
            static get properties() {
                return {
                    objItem: {
                        type: Object,
                    },
                    bootstrapCss: {
                        type: String
                    },
                    bootstrapJs: {
                        type: String
                    },
                    jqueryJs: {
                        type: String
                    }
                }
            }
            constructor() {
                super();
            }
            ready() {
                super.ready()
                this.objItem.corrections = this.objItem.corrections.split(',')
                let element_table = this.shadowRoot.querySelector('#table_test tbody');
                const replacement = '<span class="bg-warning">PLACEHOLDER</span>'

                for (let i = 0; i < this.objItem.corrections.length; i++) {
                    let correction = this.objItem.corrections[i].trim();
                    let position_of_first_difference = -1;
                    if(i > 0)
                    {
                        let string_a = correction;
                        let string_b = this.objItem.corrections[i-1].trim();
                        position_of_first_difference = get_position_of_first_difference(string_a, string_b);
                    }

                    if(position_of_first_difference != -1)
                    {
                        correction[position_of_first_difference]
                        const replacement_custom = replacement.replace('PLACEHOLDER', correction[position_of_first_difference])
                        correction = correction.substr(0, position_of_first_difference) + replacement_custom + correction.substr(position_of_first_difference + 1)
                    }

                    let row = element_table.insertRow(-1);
                    let cell1 = row.insertCell(0);
                    cell1.innerHTML = i+1;
                    let cell2 = row.insertCell(1);
                    cell2.innerHTML = correction;
                    // let row_new = `
                    //     <tr>
                    //         <td>`+(i+1)+`</td>
                    //         <td>`+correction+`</td>
                    //     </tr>
                    // `
                    // element_table.innerHTML = element_table.innerHTML + row_new;
                }
            }
        }
        customElements.define(ViewerTemplate.is, ViewerTemplate);
    </script>

</dom-module>
"""
    # 'template_path': """../corpora/template_query_speller.html"""
}
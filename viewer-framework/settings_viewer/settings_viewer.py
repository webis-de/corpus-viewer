DICT_SETTINGS_VIEWER = {
	# possible values: 'database', 'csv-file', 'ldjson-file'
	'data_type': 'database', 
		# path to file, only necessary if data_type is not 'database'
		'data_path': '',
		# name of the model, only necessary if data_type is 'database'
		'model_name': 'm_Tag',
	'data_fields': {
		'content': {
			'id': 'content',
			'type': 'string',
		},
		'count_of_something': {
			'id': 'count_of_something',
			'type': 'int',
		}
	},
	# Possible filter types: 'text', 'checkbox'
	# 
	'filters': [
		{
			'type': 'checkbox', 
			'data_field_id': 'count_of_something', 
			'description': 'Some Checkbox', 
			'default_value': '',
		},
		{
			'type': 'text', 
			'data_field_id': 'content', 
			'description': 'Some Text Input', 
			'placeholder': 'Text Input',
			'default_value': '',
		},
	],
}
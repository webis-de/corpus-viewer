def load_data():
	data = []
	
	data.append({'id': 1, 'name': 'test', 'count_of_something': 2})

	return data

DICT_SETTINGS_VIEWER = {
	# possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
	'data_type': 'ldjson-file',
		# only necessary if data_type is '*-file' or 'custom'
			# path to data,
			# 'data_path': '../corpora/webis-cbc-16',
			'data_path': '../corpora/file.ldjson',
			# structure of data in file
			'data_structure': ['name', 'count_of_something', 'id'],


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
		'name': {
			'type': 'string',
			'display_name': 'Text'
		},
		'count_of_something': {
			'type': 'int',
			'display_name': 'Retweets'
		}
	},
	'id': 'id',
	'displayed_fields': [
		'id', 'count_of_something', 'name',
	],
	'page_size': 25,
	# Possible filter types: 'text', 'checkbox'
	#
	'filters': [
		# {
		# 	'type': 'checkbox',
		# 	'data_field_name': 'count_of_something',
		# 	'description': 'Some Checkbox',
		# 	'default_value': False,
		# 	'event': 'change'
		# },
		{
			'type': 'text',
			'data_field': 'text',
			'description': 'Tweet Text',
			'placeholder': 'Text Input',
			'default_value': '',
			'event': 'input'
		},
		{
			'type': 'text',
			'data_field': 'retweet_count',
			'description': 'Count Retweets',
			'placeholder': 'Count Input',
			'default_value': '',
			'event': 'change'
		},
	],
}
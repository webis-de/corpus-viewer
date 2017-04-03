DICT_SETTINGS_VIEWER = {
	# possible values: 'database', 'csv-file', 'ldjson-file', 'directory'
	'data_type': 'database',
		# only necessary if data_type is '*-file'
			# path to data,
			'data_path': '../corpora/webis-cbc-16',
			# 'data_path': 'file.csv',
			# structure of data in file
			# 'data_structure': ['name', 'count_of_something', 'id'],


		# only necessary if data_type is 'database'
			# name of the app where the model is located
			'app_label': 'example_app',
			# name of the model
			'model_name': 'Example_Model',
	'use_cache': False,
	'data_fields': {
		'id': {
			'name': 'id',
			'type': 'int',
			'display_name': 'ID'
		},
		'name': {
			'name': 'name',
			'type': 'string',
			'display_name': 'Text'
		},
		'count_of_something': {
			'name': 'count_of_something',
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
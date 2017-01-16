DICT_SETTINGS_VIEWER = {
	# possible values: 'database', 'csv-file', 'ldjson-file'
	'data_type': 'csv-file',
		# only necessary if data_type is '*-file'
			# path to file,
			'data_path': 'csv-file.csv',
			# structure of data in file
			'data_structure': ['name', 'count_of_something'],
		# only necessary if data_type is 'database'
			# name of the app where the model is located
			'app_label': 'viewer',
			# name of the model
			'model_name': 'Example_Model',
	'data_fields': {
		'name': {
			'id': 'name',
			'type': 'string',
			'display_name': 'Content'
		},
		'count_of_something': {
			'id': 'count_of_something',
			'type': 'int',
			'display_name': 'Count'
		}
	},
	'displayed_fields': [
		'name', 'count_of_something'
	],
	# Possible filter types: 'text', 'checkbox'
	#
	'filters': [
		# {
		# 	'type': 'checkbox',
		# 	'data_field_id': 'count_of_something',
		# 	'description': 'Some Checkbox',
		# 	'default_value': '',
		# 	'event': 'change'
		# },
		# {
		# 	'type': 'text',
		# 	'data_field_id': 'name',
		# 	'description': 'Some Text Input',
		# 	'placeholder': 'Text Input',
		# 	'default_value': '',
		# 	'event': 'change'
		# },
	],
}
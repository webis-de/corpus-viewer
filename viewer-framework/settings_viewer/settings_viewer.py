DICT_SETTINGS_VIEWER = {
	# possible values: 'database', 'csv-file', 'ldjson-file', 'directory'
	'data_type': 'directory',
		# only necessary if data_type is '*-file'
			# path to data,
			'data_path': '../corpora/webis-cbc-16',
			# 'data_path': 'file.csv',
			# structure of data in file
			# 'data_structure': ['name', 'count_of_something', 'id'],


			 'data_structure': [
			 	{
					'type': ('folder', 1, 1), 
					'name': 'problems', 
					'content': [
						{
							'type': ('folder', 0, '*'),
							'name': 'viewer__field__id',
							'is_item': True,
							'content': [
								{
									'type': ('file-json', 1, 1),
									'name': 'viewer__field__id',
									'keys': [
										('id', 'id'),
										('text', 'text'),
										('retweet_count', 'retweet_count')
									]
								}
							]
						}
					]
				}
			],


		# only necessary if data_type is 'database'
			# name of the app where the model is located
			'app_label': 'example_app',
			# name of the model
			'model_name': 'Example_Model',
	'use_cache': True,
	'data_fields': {
		'id': {
			'name': 'id',
			'type': 'int',
			'display_name': 'ID'
		},
		'text': {
			'name': 'name',
			'type': 'string',
			'display_name': 'Text'
		},
		'retweet_count': {
			'name': 'retweet_count',
			'type': 'int',
			'display_name': 'Retweets'
		}
	},
	'id': 'id',
	'displayed_fields': [
		'id', 'retweet_count', 'text',
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
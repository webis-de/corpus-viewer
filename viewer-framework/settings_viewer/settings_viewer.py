import os
import csv
import json

def load_data():
	data = []
	
	path_corpora = '../corpora/webis-cbc-16'
	path_truth = os.path.join(path_corpora, 'truth')
	path_problems = os.path.join(path_corpora, 'problems')

	with open(os.path.join(path_truth, 'annotatorA.csv'), 'r') as f:
		for line in f:
			pass

	for folder in os.listdir(path_problems):
		path_problem = os.path.join(path_problems, folder)
		for file in os.listdir(path_problem):
			path_file = os.path.join(path_problem, file)
			if file.endswith('.json'):
				with open(path_file, 'r') as f:
					obj_json = json.loads(f.read())
					obj_tweet = {}
					obj_tweet['id'] = obj_json['id']
					obj_tweet['name'] = obj_json['text']
					obj_tweet['count_of_something'] = obj_json['retweet_count']
					data.append(obj_tweet)
		# break 


	return data

DICT_SETTINGS_VIEWER = {
	# possible values: 'csv-file', 'ldjson-file', 'custom', 'database'
	'data_type': 'custom',
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
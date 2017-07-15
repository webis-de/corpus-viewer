from .Handle_Index import * 

class Handle_Index_Dictionary(Handle_Index):
	def __init__(self, id_corpus, settings_corpus):
		self.id_corpus = id_corpus
		self.settings_corpus = settings_corpus
		self.dict_data = {}

	def add_string(self, data_field, key, value):
		try:
			# self.dict_data[key] = set()
			print("added string")
			print(data_field)
			self.dict_data[key].add(value)
		except KeyError:
			self.dict_data[key] = set()
			self.dict_data[key].add(value)

	def add_text(self, data_field, key, value):
		try:
			# self.dict_data[key] = set()
			print("added text")
			print(data_field)
			self.dict_data[key].add(value)
		except KeyError:
			self.dict_data[key] = set() 
			self.dict_data[key].add(value)

	def add_number(self, data_field, key, value):
		try:
			# self.dict_data[key] = set()
			print("added number")
			print(data_field)
			self.dict_data[key].add(value)
		except KeyError:
			self.dict_data[key] = set() 
			self.dict_data[key].add(value)
		
	def get(self, data_field, key):
		try:
			print(key)
			print(self.dict_data)
			return self.dict_data[key]
		except KeyError:
			return set()
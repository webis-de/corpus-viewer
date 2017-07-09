from .Handle_Index import * 

class Handle_Index_Dictionary(Handle_Index):
	def __init__(self):
		self.dict_data = {}

	def add_string(self, key, value):
		try:
			# self.dict_data[key] = set()
			print("added string")
			self.dict_data[key].add(value)
		except KeyError:
			self.dict_data[key] = set() 
			self.dict_data[key].add(value)

	def add_text(self, key, value):
		try:
			# self.dict_data[key] = set()
			print("added text")
			self.dict_data[key].add(value)
		except KeyError:
			self.dict_data[key] = set() 
			self.dict_data[key].add(value)

	def add_number(self, key, value):
		try:
			# self.dict_data[key] = set()
			print("added number")
			self.dict_data[key].add(value)
		except KeyError:
			self.dict_data[key] = set() 
			self.dict_data[key].add(value)
		
	def get(self, key):
		try:
			print(key)
			print(self.dict_data)
			return self.dict_data[key]
		except KeyError:
			return set()
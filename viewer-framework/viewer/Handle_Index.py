class Handle_Index():
	def __init__(self):
		self.dict_data = {}

	def add(self, key, value):
		try:
			self.dict_data[key] = set()
			print("worked")
			self.dict_data[key].add(value)
		except KeyError:
			self.dict_data[key] = set(value)

	def get(self, key):
		try:
			print(key)
			print(self.dict_data)
			return self.dict_data[key]
		except KeyError:
			return set()

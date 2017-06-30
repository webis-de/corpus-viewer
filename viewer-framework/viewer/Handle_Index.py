class Handle_Index():
	def __init__(self):
		self.dict_data = {}

	def add(self, key, value):
		try:
			self.dict_data[key].append(value)
		except KeyError:
			self.dict_data[key] = [value]

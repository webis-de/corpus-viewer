from abc import ABC, abstractmethod

class Handle_Index(ABC):
	@abstractmethod
	def add_string(self, data_field, value, id_intern):
		pass

	@abstractmethod
	def add_text(self, data_field, value, id_intern):
		pass

	@abstractmethod
	def add_number(self, data_field, value, id_intern):
		pass

	@abstractmethod
	def get(self, data_field, value):
		pass

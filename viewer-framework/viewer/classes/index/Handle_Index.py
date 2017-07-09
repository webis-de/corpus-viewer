from abc import ABC, abstractmethod

class Handle_Index(ABC):
	@abstractmethod
	def add_string(self, value, id_intern):
		pass

	@abstractmethod
	def add_text(self, value, id_intern):
		pass

	@abstractmethod
	def add_number(self, value, id_intern):
		pass

	@abstractmethod
	def get(self, value):
		pass

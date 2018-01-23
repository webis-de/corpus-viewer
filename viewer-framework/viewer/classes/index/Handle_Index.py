from abc import ABC, abstractmethod

class Handle_Index(ABC):
    def __init__(self, id_corpus, settings_corpus):
        self.id_corpus = id_corpus
        self.settings_corpus = settings_corpus

    @staticmethod
    @abstractmethod
    def is_active():
        pass

    @staticmethod
    @abstractmethod
    def get_display_name():
        pass

    @staticmethod
    @abstractmethod
    def get_description():
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def finish(self):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def add_item(self, id_intern, item):
        pass

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
    def get_string(self, data_field, value, case_sensitive):
        pass

    @abstractmethod
    def get_boolean(self, data_field, value):
        pass

    @abstractmethod
    def get_text(self, data_field, value, case_sensitive):
        pass

    @abstractmethod
    def get_number(self, data_field, value):
        pass

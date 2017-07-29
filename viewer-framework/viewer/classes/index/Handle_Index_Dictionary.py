from .Handle_Index import * 

class Handle_Index_Dictionary(Handle_Index):
    def __init__(self, id_corpus, settings_corpus):
        Handle_Index.__init__(self, id_corpus, settings_corpus)

        self.dict_data = {}
        for key, value in self.settings_corpus['data_fields'].items():
            self.dict_data[key] = {}
    
    def is_active():
        return False
    
    def get_display_name():
        return 'Dictionary'

    def get_description():
        return 'test html'

    def start(self):
        pass

    def finish(self):
        pass
        
    def add_item(self, id_intern, item):
        pass

    def add_string(self, data_field, key, value):
        try:
            # print("added string")
            # print(data_field)
            self.dict_data[data_field][key].append(value)
        except KeyError:
            self.dict_data[data_field][key] = [value]

    def add_text(self, data_field, key, value):
        try:
            # print("added text")
            # print(data_field)
            self.dict_data[data_field][key].append(value)
        except KeyError:
            self.dict_data[data_field][key] = [value] 

    def add_number(self, data_field, key, value):
        try:
            # print("added number")
            # print(data_field)
            self.dict_data[data_field][key].append(value)
        except KeyError:
            self.dict_data[data_field][key] = [value] 

    def get_string(self, data_field, value, case_sensitive):
        try:
            # print(key)
            # print(self.dict_data[data_field])
            return self.dict_data[data_field][value]
        except KeyError:
            return []

    def get_text(self, data_field, value, case_sensitive):
        try:
            # print(key)
            # print(self.dict_data[data_field])
            return self.dict_data[data_field][value]
        except KeyError:
            return []

    def get_number(self, data_field, value):
        try:
            # print(key)
            # print(self.dict_data[data_field])
            return self.dict_data[data_field][value]
        except KeyError:
            return []

    def clear(self):
        self.dict_data = {}
        for key, value in self.settings_corpus['data_fields'].items():
            self.dict_data[key] = {}
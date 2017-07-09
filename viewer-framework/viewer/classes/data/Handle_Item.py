import pickle
import struct

class Handle_Item:
    def __init__(self, struct):
        self.struct = struct

class Handle_Item_Get_Item(Handle_Item):
    def __init__(self, struct, length_struct, handle_file_data, handle_file_metadata):
        Handle_Item.__init__(self, struct)

        self.length_struct = length_struct
        self.handle_file_data = handle_file_data
        self.handle_file_metadata = handle_file_metadata

    def get_items(self, list_indices):
        list_items = []
        for index in list_indices:
            offset_in_bytes_metadata = index * self.length_struct

            self.handle_file_metadata.seek(offset_in_bytes_metadata)
            item_bin = self.handle_file_metadata.read(self.length_struct)
            metadata = self.struct.unpack(item_bin) 

            self.handle_file_data.seek(metadata[0])
            item_bin = self.handle_file_data.read(metadata[1])

            list_items.append(pickle.loads(item_bin))

        return list_items

# class Handle_Item_Get_Metadata(Handle_Item):
#     def __init__(self, struct, length_struct, handle_file_metadata):
#         Handle_Item.__init__(self, struct)

#         self.length_struct = length_struct
#         self.handle_file_metadata = handle_file_metadata

    # def get(self, list_items):
        # print(list_items)
        # for item in list_items:
            # print(item)
        # offset_in_bytes = index * self.length_struct

        # self.handle_file_metadata.seek(offset_in_bytes)
        # item_bin = self.handle_file_metadata.read(self.length_struct)
        # return self.struct.unpack(item_bin) 

    # def get(self, index, length_in_bytes):
    #     offset_in_bytes = index * 19

    #     self.handle_file_metadata.seek(offset_in_bytes)
    #     item_bin = self.handle_file_metadata.read(19)
    #     return pickle.loads(item_bin)
    #     # return self.struct.unpack(item_bin)

class Handle_Item_Add(Handle_Item):
    def __init__(self, struct, handle_index, handle_file_data, handle_file_metadata, dict_data, field_id, dict_data_fields):
        Handle_Item.__init__(self, struct) 

        self.handle_file_data = handle_file_data
        self.handle_file_metadata = handle_file_metadata
        self.dict_data = dict_data
        self.field_id = field_id
        # self.settings_corpus = settings_corpus
        self.dict_data_fields = dict_data_fields
        self.handle_index = handle_index

    def add(self, item):
        # print(self.dict_data)
        bin_item = pickle.dumps(item)
        self.handle_file_data.write(bin_item)

        id_intern = self.dict_data['size']

        length_in_bytes = len(bin_item)

        bin_metadata = self.struct.pack(self.dict_data['size_in_bytes'], length_in_bytes)
        self.handle_file_metadata.write(bin_metadata)

        for key, data_field in self.dict_data_fields.items():
        # for key, data_field in self.settings_corpus['data_fields'].items():
            pass
            # type_data_field = data_field['type']
            # value = item[key]

            # if type_data_field == 'string':
            #     self.handle_index.add_string(value, id_intern)
            # elif type_data_field == 'text':
            #     self.handle_index.add_text(value, id_intern)
            # elif type_data_field == 'number':
            #     self.handle_index.add_number(value, id_intern)

        # self.dict_data['list'].append(id_intern)
        # self.dict_data['list'].append((self.dict_data['size'], item[self.field_id]))
        self.dict_data['size'] += 1
        self.dict_data['size_in_bytes'] += length_in_bytes

    # def add(self, item):
    #     item_bin = pickle.dumps(item)
    #     length_in_bytes = len(item_bin)
    #     # self.handle_file_data.write(item_bin)
    #     # try:
    #     item_bin = pickle.dumps((self.dict_data['size_in_bytes'], length_in_bytes, self.dict_data['size']))
    #     # item_bin = self.struct.pack(self.dict_data['size_in_bytes'], length_in_bytes, self.dict_data['size'])
    #     # except:
    #     #     print(self.dict_data['size_in_bytes'])
    #     #     print(length_in_bytes)
    #     #     print(self.dict_data['size'])
    #     self.handle_file_metadata.write(item_bin)

    #     self.dict_data['list'].append(len(item_bin))
    #     self.dict_data['size'] += 1
    #     self.dict_data['size_in_bytes'] += length_in_bytes
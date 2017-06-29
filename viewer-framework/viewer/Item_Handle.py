import pickle
import struct

class Item_Handle:
    def __init__(self, dict_data, id_corpus, handle_file_data, handle_file_metadata, field_id):
        self.dict_data = dict_data
        self.id_corpus = id_corpus
        self.handle_file_data = handle_file_data
        self.handle_file_metadata = handle_file_metadata
        self.field_id = field_id

        self.struct = struct.Struct('<Q Q Q')
        self.length_struct = 24

    def add(self, item):
        # print(self.dict_data)
        item_bin = pickle.dumps(item)
        length_in_bytes = len(item_bin)

        # self.handle_file_data.write(item_bin)
        # try:
        item_bin = self.struct.pack(self.dict_data['size_in_bytes'], length_in_bytes, self.dict_data['size'])
        # except:
        #     print(self.dict_data['size_in_bytes'])
        #     print(length_in_bytes)
        #     print(self.dict_data['size'])
        self.handle_file_metadata.write(item_bin)

        self.dict_data['list'].append(item[self.field_id])
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

    def get(self, index):
        offset_in_bytes = index * self.length_struct

        self.handle_file_metadata.seek(offset_in_bytes)
        item_bin = self.handle_file_metadata.read(self.length_struct)
        return self.struct.unpack(item_bin)

    # def get(self, index, length_in_bytes):
    #     offset_in_bytes = index * 19

    #     self.handle_file_metadata.seek(offset_in_bytes)
    #     item_bin = self.handle_file_metadata.read(19)
    #     return pickle.loads(item_bin)
    #     # return self.struct.unpack(item_bin)

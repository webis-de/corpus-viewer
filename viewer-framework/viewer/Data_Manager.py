from django.core.cache import cache
from .Item_Handle import *
from .Handle_Index import *
import time
import os
import shelve

class Data_Manager:
    def __init__(self, glob_settings):
        self.debug = True
        self.path_cache = '../cache'
        self.struct = struct.Struct('<Q Q Q')
        self.length_struct = self.struct.size
        self.handle_index = Handle_Index()
        self.dict_data = self.init_data()

        if not os.path.exists(self.path_cache):
            os.mkdir(self.path_cache)

    def init_data(self):
        dict_data = cache.get('metadata_corpora')
        if(dict_data == None):
            dict_data = {}

        return dict_data

    def index_corpus(self, id_corpus, settings_corpus):
        if self.debug == True:
            print('indexing \''+id_corpus+'\'')

        field_id = settings_corpus['id']

        dict_data = {}
        dict_data['is_loaded'] = False
        dict_data['size'] = 0
        dict_data['size_in_bytes'] = 0
        dict_data['list'] = []

        self.dict_data[id_corpus] = dict_data

        path_corpus = os.path.join(self.path_cache, id_corpus)
        if not os.path.exists(path_corpus):
            os.mkdir(path_corpus)

        with open(os.path.join(path_corpus, id_corpus + '.data'), 'wb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'wb') as handle_file_metadata:
                start = time.perf_counter()
                obj_item_handle = Item_Handle_Add(self.struct, self.handle_index, handle_file_data, handle_file_metadata, dict_data, field_id, settings_corpus)

                settings_corpus['load_data_function'](obj_item_handle)
                print('writing time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

        # cache.set('metadata_corpora', glob_cache)

        print('size of corpus: '+str(dict_data['size']))
        print('size of corpus (bytes): '+str(dict_data['size_in_bytes']))
        print('')
        # print(self.handle_index.dict_data)

        # with open(os.path.join(path_corpus, id_corpus + '_metadata.pickle'), 'rb') as handle_file_metadata:
        #     start = time.perf_counter()
        #     obj_item_handle = Item_Handle_Get_Metadata(self.struct, self.length_struct, handle_file_metadata)

        #     for index, item in enumerate(dict_data['list']):   
        #         obj_item_handle.get(index)
        #     print('loading time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

        dict_data['is_loaded'] = True
        # self.dict_data[id_corpus] = dict_data
        # print(dict_data)
        return dict_data

    def get_all_ids_for_corpus(self, id_corpus, settings_corpus):
        if self.debug == True:
            print('loading all ids from \''+id_corpus+'\'')

        try:
            return self.dict_data[id_corpus]['list']
        except KeyError:
            if self.debug == True:
                print('no entry for \''+id_corpus+'\' found')
            return self.index_corpus(id_corpus, settings_corpus)['list']

    def get_items(self, id_corpus, corpus, list_indices):       
        path_corpus = os.path.join(self.path_cache, id_corpus)

        with open(os.path.join(path_corpus, id_corpus + '.data'), 'rb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'rb') as handle_file_metadata:
                obj_item_handle = Item_Handle_Get_Item(self.struct, self.length_struct, handle_file_data, handle_file_metadata)
                return obj_item_handle.get_items(list_indices)

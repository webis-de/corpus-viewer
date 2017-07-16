from django.core.cache import cache
from .Handle_Item import *
from ..index.Handle_Index_Dictionary import Handle_Index_Dictionary
from enum import IntEnum, unique
import time
import os
import shutil

class Manager_Data:
    def __init__(self):
        self.debug = True
        self.path_cache = '../cache'
        self.struct = struct.Struct('<Q L')
        self.length_struct = self.struct.size
        self.manager_corpora = Manager_Corpora()
        self.dict_data = self.init_data()

        if not os.path.exists(self.path_cache):
            os.mkdir(self.path_cache)

    def init_data(self):
        dict_data = cache.get('metadata_corpora')
        if(dict_data == None):
            dict_data = {}
        else:
            dict_tmp = {}
            for id_corpus in self.manager_corpora.get_ids_corpora():
                try:
                    dict_tmp[id_corpus] = dict_data[id_corpus]
                except KeyError:
                    pass

            dict_data = dict_tmp

            self.update_cache(dict_data)

            for key in dict_data.keys():
                print(key)
                print(key)
                print(key)
            
        
        if self.debug == True:
            print('loaded metadata for {} corpora'.format(len(dict_data)))

            # dict_data[key]['handle_index'] = Handle_Index_Dictionary(id_corpus, settings_corpus)

        return dict_data

    def update_cache(self, dict_data):
        list_keys = ['is_loaded', 'size', 'size_in_bytes']

        dict_data = {key:dict_data[key] for key in list_keys}
        cache.set('metadata_corpora', dict_data)

    def delete_corpus(self, id_corpus):
        path_corpus = os.path.join(self.path_cache, id_corpus)
        shutil.rmtree(path_corpus)

        del self.dict_data[id_corpus]
        self.update_cache(self.dict_data)

        self.manager_corpora.delete_corpus(id_corpus)

    def get_number_of_indexed_items(self, id_corpus):
        return self.dict_data[id_corpus]['size']

    def reindex_corpus(self, id_corpus):
        settings_corpus = self.manager_corpora.reload_settings(id_corpus)
        self.index_corpus(id_corpus, settings_corpus)

    def index_corpus(self, id_corpus, settings_corpus):
        if self.debug == True:
            print('indexing \''+id_corpus+'\'')

        field_id = settings_corpus['id']

        dict_data = {}
        dict_data['is_loaded'] = False
        dict_data['size'] = 0
        dict_data['size_in_bytes'] = 0
        
        handle_index = Handle_Index_Dictionary(id_corpus, settings_corpus)
        # dict_data['handle_index'] = handle_index

        self.dict_data[id_corpus] = dict_data
        # cache.set('metadata_corpora', self.dict_data)

        path_corpus = os.path.join(self.path_cache, id_corpus)
        if not os.path.exists(path_corpus):
            os.mkdir(path_corpus)

        with open(os.path.join(path_corpus, id_corpus + '.data'), 'wb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'wb') as handle_file_metadata:
                start = time.perf_counter()
                obj_handle_item = Handle_Item_Add(self.struct, handle_index, handle_file_data, handle_file_metadata, dict_data, field_id, settings_corpus['data_fields'])

                settings_corpus['load_data_function'](obj_handle_item)
                print('writing time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

        # cache.set('metadata_corpora', glob_cache)

        print('size of corpus: '+str(dict_data['size']))
        print('size of corpus (bytes): '+str(dict_data['size_in_bytes']))
        print('')
        # print(self.handle_index.dict_data)

        # with open(os.path.join(path_corpus, id_corpus + '_metadata.pickle'), 'rb') as handle_file_metadata:
        #     start = time.perf_counter()
        #     obj_handle_item = Item_Handle_Get_Metadata(self.struct, self.length_struct, handle_file_metadata)

        #     for index, item in enumerate(dict_data['list']):   
        #         obj_handle_item.get(index)
        #     print('loading time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
        print('made this')
        dict_data['is_loaded'] = True
        self.update_cache(self.dict_data)
        # cache.set('metadata_corpora', self.dict_data)
        print(self.dict_data)

        # self.dict_data[id_corpus] = dict_data
        # print(dict_data)

    def get_all_ids_for_corpus(self, id_corpus, settings_corpus):
        if self.debug == True:
            print('loading all ids from \''+id_corpus+'\'')

        try:
            return range(0, self.dict_data[id_corpus]['size'])
        except KeyError:
            if self.debug == True:
                print('no entry for \''+id_corpus+'\' found')
            return []
            # self.index_corpus(id_corpus, settings_corpus)
            # return range(0, self.dict_data[id_corpus]['size'])

    def get_items(self, id_corpus, corpus, list_indices):       
        path_corpus = os.path.join(self.path_cache, id_corpus)

        with open(os.path.join(path_corpus, id_corpus + '.data'), 'rb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'rb') as handle_file_metadata:
                obj_handle_item = Handle_Item_Get_Item(self.struct, self.length_struct, handle_file_data, handle_file_metadata)
                return obj_handle_item.get_items(list_indices)


    def get_state_loaded(self, id_corpus):       
        state_loaded = self.State_Loaded.NOT_LOADED

        if id_corpus in self.dict_data:
            if self.dict_data[id_corpus]['is_loaded'] == True:
                state_loaded = self.State_Loaded.LOADED
            else:
                state_loaded = self.State_Loaded.LOADING

        return state_loaded

    @unique
    class State_Loaded(IntEnum):
        LOADED = 0
        NOT_LOADED = 1
        LOADING = 2
    
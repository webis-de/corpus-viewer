from django.core.cache import cache
from .Handle_Item import *
from ..index.Handle_Index_Whoosh import Handle_Index_Whoosh as Handle_Index
# from ..index.Handle_Index_Dictionary import Handle_Index_Dictionary as Handle_Index
from enum import IntEnum, unique
import time
import os
import shutil

class Manager_Data:
    def __init__(self):
        self.debug = True
        self.path_settings = '../settings'
        self.path_backup = 'backup_settings'
        self.path_cache = '../cache'
        self.struct = struct.Struct('<Q L')
        self.length_struct = self.struct.size
        self.dict_corpora = {}

        self.init_data()

    def init_data(self):
        self.create_paths_if_necessary()
        
        for file in os.listdir(self.path_settings):
            id_corpus = file[:-3]
            self.dict_corpora[id_corpus] =  {}
            self.dict_corpora[id_corpus]['settings'] = self.load_corpus_from_file(file)
            self.dict_corpora[id_corpus]['handle_index'] = Handle_Index(id_corpus, self.get_settings_for_corpus(id_corpus))

        dict_corpora_cached = cache.get('metadata_corpora')
        if(dict_corpora_cached != None):
            for id_corpus in self.dict_corpora.keys():
                try:
                    self.dict_corpora[id_corpus].update(dict_corpora_cached[id_corpus])
                except KeyError:
                    print('SOME ERROR HAPPENEND')
        else:
            dict_tmp = {
                'size_in_bytes': 0, 
                'size': 0, 
                'state_loaded': self.State_Loaded.NOT_LOADED
            }
            for id_corpus in self.dict_corpora.keys():
                self.dict_corpora[id_corpus].update(dict_tmp)

        self.update_cache()
        
        if self.debug == True:
            print('loaded metadata for {} corpora'.format(len(self.dict_corpora)))

        #     # dict_corpora_cached[key]['handle_index'] = Handle_Index(id_corpus, settings_corpus)

    def get_ids_corpora(self, sorted_by=None):
        if sorted_by == None:
            return self.dict_corpora.keys()
        elif sorted_by == 'name':
            return sorted(self.dict_corpora.keys(), key=lambda id_corpus: self.dict_corpora[id_corpus]['settings']['name'])

    def load_corpus_from_file(self, file):
        with open(os.path.join(self.path_settings, file), 'r') as f:
            compiled = compile(f.read(), '<string>', 'exec')
            global_env = {}
            local_env = {}
            exec(compiled, global_env, local_env)

            if self.debug == True:
                print('parsed settings for \'{}\''.format(file))

        return local_env['DICT_SETTINGS_VIEWER']

    def create_paths_if_necessary(self):
        if not os.path.exists(self.path_settings):
            os.mkdir(self.path_settings)

        if not os.path.exists(self.path_backup):
            os.mkdir(self.path_backup)

        if not os.path.exists(self.path_cache):
            os.mkdir(self.path_cache)

    def update_cache(self):
        list_keys = ['state_loaded', 'size', 'size_in_bytes']

        dict_tmp = {}
        for id_corpus, value in self.dict_corpora.items():
            dict_tmp[id_corpus] = {key: self.dict_corpora[id_corpus][key] for key in list_keys}

        cache.set('metadata_corpora', dict_tmp)

    def set_current_corpus(self, request):
        default = list(self.dict_corpora.keys())[0]
        key = 'viewer__current_corpus'
        sessionkey = 'viewer__' + key

        if request.GET.get(key) != None:
            request.session[sessionkey] = request.GET.get(key)
        else:
            if sessionkey not in request.session:
                try:
                    request.session[sessionkey] = list(self.dict_corpora.keys())[0]
                except:
                    raise('NO CORPUS FOUND')

    def get_setting_for_corpus(self, key, id_corpus):
        settings_corpus = self.dict_corpora[id_corpus]['settings']
        if key in settings_corpus:
            return settings_corpus[key]

        if key == 'use_cache':
            return False;
        elif key == 'page_size':
            return 25;

        raise ValueError('setting-key \''+key+'\' not found')

    def get_settings_for_corpus(self, id_corpus):
        return self.dict_corpora[id_corpus]['settings']

    def reload_settings(self, id_corpus):
        file = id_corpus + '.py'
        settings = self.load_corpus_from_file(file)
        self.dict_corpora[id_corpus]['settings'] = settings

        return settings

    def check_for_new_corpora(self):
        dict_tmp = {}

        for file in os.listdir(self.path_settings):
            id_corpus = file[:-3]

            try:
                dict_tmp[id_corpus] = self.dict_corpora[id_corpus]
            except KeyError:
                dict_tmp[id_corpus] = {'size_in_bytes': 0, 'size': 0, 'state_loaded': self.State_Loaded.NOT_LOADED}
                dict_tmp[id_corpus]['handle_index'] = Handle_Index(id_corpus, self.get_settings_for_corpus(id_corpus))

                dict_tmp[id_corpus]['settings'] = self.load_corpus_from_file(file)

        self.dict_corpora = dict_tmp
        self.update_cache()

    def delete_corpus(self, id_corpus):
        path_corpus = os.path.join(self.path_cache, id_corpus)
        shutil.rmtree(path_corpus)

        del self.dict_corpora[id_corpus]
        self.update_cache()

        file = id_corpus + '.py'
        path_settings = os.path.join(self.path_settings, file)
        path_settings_destination = os.path.join(self.path_backup, file)
        shutil.move(path_settings, path_settings_destination)

    def get_number_of_indexed_items(self, id_corpus):
        return self.dict_corpora[id_corpus]['size']

    def reindex_corpus(self, id_corpus):
        settings_corpus = self.reload_settings(id_corpus)
        self.index_corpus(id_corpus, settings_corpus)

    def get_handle_index(self, id_corpus):
        return self.dict_corpora[id_corpus]['handle_index']

    def index_corpus(self, id_corpus, settings_corpus):
        if self.debug == True:
            print('indexing \''+id_corpus+'\'')

        field_id = settings_corpus['id']

        self.dict_corpora[id_corpus]['state_loaded'] = self.State_Loaded.LOADING
        self.dict_corpora[id_corpus]['size'] = 0
        self.dict_corpora[id_corpus]['size_in_bytes'] = 0

        handle_index = self.dict_corpora[id_corpus]['handle_index']
        handle_index.clear()

        
        # cache.set('metadata_corpora', self.dict_data)

        handle_index.start()
        path_corpus = os.path.join(self.path_cache, id_corpus)
        if not os.path.exists(path_corpus):
            os.mkdir(path_corpus)

        with open(os.path.join(path_corpus, id_corpus + '.data'), 'wb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'wb') as handle_file_metadata:
                start = time.perf_counter()
                obj_handle_item = Handle_Item_Add(self.struct, handle_file_data, handle_file_metadata, self.dict_corpora[id_corpus], field_id, settings_corpus['data_fields'])

                settings_corpus['load_data_function'](obj_handle_item)
                print('writing time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

        # cache.set('metadata_corpora', glob_cache)
        handle_index.finish()

        
        print('size of corpus: '+str(self.dict_corpora[id_corpus]['size']))
        print('size of corpus (bytes): '+str(self.dict_corpora[id_corpus]['size_in_bytes']))
        print('')
        # print(self.handle_index.dict_data)

        # with open(os.path.join(path_corpus, id_corpus + '_metadata.pickle'), 'rb') as handle_file_metadata:
        #     start = time.perf_counter()
        #     obj_handle_item = Item_Handle_Get_Metadata(self.struct, self.length_struct, handle_file_metadata)

        #     for index, item in enumerate(dict_data['list']):   
        #         obj_handle_item.get(index)
        #     print('loading time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')
        self.dict_corpora[id_corpus]['state_loaded'] = self.State_Loaded.LOADED
        self.update_cache()

        # print(self.dict_corpora[id_corpus]['handle_index'].dict_data)
        # cache.set('metadata_corpora', self.dict_data)

        # self.dict_data[id_corpus] = dict_data
        # print(dict_data)

    def get_all_ids_for_corpus(self, id_corpus, settings_corpus):
        if self.debug == True:
            print('loading all ids from \''+id_corpus+'\'')

        try:
            return range(0, self.dict_corpora[id_corpus]['size'])
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
        return self.dict_corpora[id_corpus]['state_loaded']

    @unique
    class State_Loaded(IntEnum):
        LOADED = 0
        NOT_LOADED = 1
        LOADING = 2
    
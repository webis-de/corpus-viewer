from django.core.cache import cache
from .Handle_Item import *
from .Corpus import *
import glob
import importlib
import os
import csv
import json
import traceback
import sys
import pprint
from django.conf import settings
import errno, stat

modules = glob.glob(os.path.join(settings.BASE_DIR, 'viewer/classes/index/Handle_Index_*.py'))
__all__ = [os.path.basename(f)[:-3] for f in modules]
dict_handle_indices = {}
for corpus in __all__:
    module_index_handle = importlib.import_module('viewer.classes.index.'+corpus)
    dict_handle_indices[corpus] = module_index_handle

# from ..index.Handle_Index_Whoosh import Handle_Index_Whoosh as Handle_Index
# from ..index.Handle_Index_Dictionary import Handle_Index_Dictionary as Handle_Index
from enum import IntEnum, unique
import time
import shutil

class Manager_Data:
    def __init__(self):
        self.debug = True
        self.dict_exceptions = {}
        self.path_settings = os.path.join(settings.BASE_DIR , '..', 'settings')
        self.path_backup = os.path.join(settings.BASE_DIR, 'backup_settings')
        self.path_cache = os.path.join(settings.BASE_DIR, '..', 'cache')
        self.struct = struct.Struct('<Q L') # position, length
        self.length_struct = self.struct.size
        self.dict_corpora = {}

        self.init_data()

    def get_default_settings(self):
        # singleton behaviour
        try:
            return self.dict_default_settings.copy()
        except AttributeError:
            self.dict_default_settings = {
                'size_in_bytes': 0, 
                'size': 0, 
                'state_loaded': self.State_Loaded.NOT_LOADED,
                'exception': None
            }
            return self.dict_default_settings.copy()

    def update_template(self, id_corpus):
        template_html = self.get_setting_for_corpus('template_html', id_corpus)
        # if no template was specified as html
        if template_html == None:
            # check if there is an path to the template
            template_path = self.get_setting_for_corpus('template_path', id_corpus)

            # if there is an path specified
            if template_path != None:
                try:
                    with open(template_path, 'r') as f:
                        self.dict_corpora[id_corpus]['settings']['template_html'] = f.read()
                except FileNotFoundError:
                    print('file not found')


            
        # self.dict_corpora[id_corpus]['template']

    def init_data(self):
        try:
            self.path_settings = settings.PATH_FILES_SETTINGS
        except AttributeError:
            pass

        try:
            self.path_cache = settings.PATH_FILES_CACHE
        except AttributeError:
            pass
            
        self.create_paths_if_necessary()
        # for every settings-file in the directory load the settings into the empty dict_corpora
        for file in os.listdir(self.path_settings):
            id_corpus = file[:-3]
            self.dict_corpora[id_corpus] =  {}
            try:
                self.dict_corpora[id_corpus]['settings'] = self.load_corpus_from_file(file)
                self.dict_corpora[id_corpus]['exception'] = None
                self.update_template(id_corpus)
            except SyntaxError as err:
                self.dict_corpora[id_corpus]['exception'] = err.lineno
                self.dict_corpora[id_corpus]['settings'] = {}

        # get the previously cached data 
        dict_corpora_cached = cache.get('metadata_corpora')
        if(dict_corpora_cached != None):
            # for each settings-file 
            for id_corpus in self.dict_corpora.keys():
                # try to get the cached data (size/state_loaded-info)
                try:
                    self.dict_corpora[id_corpus].update(dict_corpora_cached[id_corpus])
                    # if the corpus has information about the used index
                except KeyError:
                    self.dict_corpora[id_corpus].update(self.get_default_settings())
                # try to instantiate the index handle
                try:
                    self.dict_corpora[id_corpus]['handle_index'] = getattr(dict_handle_indices[self.dict_corpora[id_corpus]['class_handle_index']], self.dict_corpora[id_corpus]['class_handle_index'])(id_corpus, self.get_settings_for_corpus(id_corpus))
                    print("index handle found for "+id_corpus)
                except KeyError:
                    print("no index handle found for "+id_corpus)
        else:
            for id_corpus in self.dict_corpora.keys():
                self.dict_corpora[id_corpus].update(self.get_default_settings())

                # if self.dict_corpora[id_corpus]['settings']['data_type'] == 'database':
                #     module_custom = importlib.import_module(self.get_setting_for_corpus('app_label', id_corpus)+'.models')
                #     model_custom = getattr(module_custom, self.get_setting_for_corpus('model_name', id_corpus))
                #     self.dict_corpora[id_corpus]['size'] = model_custom.objects.filter(
                #         **self.get_setting_for_corpus('database_filters', id_corpus)
                #     ).count()

        for id_corpus, value in self.dict_corpora.items():
            print(value.keys())

        self.update_cache()
        
        if self.debug == True:
            print('loaded metadata for {} corpora'.format(len(self.dict_corpora)))

    def get_ids_corpora(self, sorted_by=None):
        list_ids_corpora = [key for key in self.dict_corpora.keys() if self.dict_corpora[key]['exception'] == None]
        print(list_ids_corpora)

        if sorted_by == None:
            return list_ids_corpora
        elif sorted_by == 'name':
            return sorted(list_ids_corpora, key=lambda id_corpus: self.dict_corpora[id_corpus]['settings']['name'].lower())

    def load_corpus_from_file(self, file):
        with open(os.path.join(self.path_settings, file), 'r') as f:
            global_env = {}
            local_env = {}

            compiled = compile(f.read(), '<string>', 'exec')
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
        list_keys = self.get_default_settings().keys()
        list_keys_optional = ['class_handle_index']

        dict_tmp = {}
        for id_corpus, value in self.dict_corpora.items():
            dict_tmp[id_corpus] = {key: self.dict_corpora[id_corpus][key] for key in list_keys}

            for key in list_keys_optional:
                try:
                    dict_tmp[id_corpus][key] =  self.dict_corpora[id_corpus][key]
                except KeyError:
                    pass

        cache.set('metadata_corpora', dict_tmp)

    def set_current_corpus(self, request, id_corpus):
        default = list(self.dict_corpora.keys())[0]
        key = 'viewer__current_corpus'
        sessionkey = 'viewer__' + key

        request.session[sessionkey] = id_corpus
        return
        if request.GET.get(key) != None:
            request.session[sessionkey] = request.GET.get(key)
        else:
            if sessionkey not in request.session:
                try:
                    request.session[sessionkey] = list(self.dict_corpora.keys())[0]
                except:
                    raise('NO CORPUS FOUND')

    def pop_exception(self, id_corpus):
        exception = self.dict_corpora[id_corpus]['exception']
        self.dict_corpora[id_corpus]['exception'] = None

        return exception

    def check_if_corpus_available(self, id_corpus):
        is_known = id_corpus in self.dict_corpora
        if not is_known:
            return False

        has_exception = self.dict_corpora[id_corpus]['exception']
        if has_exception:
            return False

        return True

    def get_has_access_to_editing(self, id_corpus, request):
        has_access_to_editing = False
        if self.has_corpus_secret_token_editing(id_corpus):
            if self.is_secret_token_editing_valid(id_corpus, ''):
                has_access_to_editing = True
            else:
                try:
                    secret_token = request.session[id_corpus]['viewer__secret_token_editing']
                except KeyError:
                    secret_token = None
                if self.is_secret_token_editing_valid(id_corpus, secret_token):
                    has_access_to_editing = True   

        return has_access_to_editing 

    # def get_has_access_to_tagging(self, id_corpus, request):
    #     has_access_to_tagging = False
    #     if self.has_corpus_secret_token_editing(id_corpus):
    #         try:
    #             secret_token = request.session[id_corpus]['viewer__secret_token_editing']
    #         except KeyError:
    #             secret_token = None
    #         if self.is_secret_token_editing_valid(id_corpus, secret_token):
    #             has_access_to_tagging = True   

    #     return has_access_to_tagging 

    # def is_editing_allowed(self, id_corpus):
    #     if not self.has_corpus_secret_token(id_corpus) and not self.has_corpus_secret_token_editing(id_corpus):
    #         return True
    #     return False
         
    def has_corpus_secret_token_editing(self, id_corpus):
        return self.get_setting_for_corpus('secret_token_editing', id_corpus) != None

    def has_corpus_secret_token(self, id_corpus):
        return self.get_setting_for_corpus('secret_token', id_corpus) != None

    def is_secret_token_editing_valid(self, id_corpus, secret_token):
        return self.get_setting_for_corpus('secret_token_editing', id_corpus) == secret_token

    def is_secret_token_valid(self, id_corpus, secret_token):
        return self.get_setting_for_corpus('secret_token', id_corpus) == secret_token

    def get_setting_for_corpus(self, key, id_corpus):
        settings_corpus = self.dict_corpora[id_corpus]['settings']
        if key in settings_corpus:
            return settings_corpus[key]

        if key == 'page_size':
            return 25
        elif key == 'filters':
            return []
        elif key == 'description':
            return ''
        elif key == 'secret_token':
            return None
        elif key == 'secret_token_editing':
            return None
        elif key == 'template_path':
            return None
        elif key == 'template_html':
            return None
        elif key == 'external_source':
            return None
        elif key == 'urls_header':
            return []
        elif key == 'database_filters':
            return {}
        elif key == 'database_prefetch_related':
            return []
        elif key == 'database_select_related':
            return []
        elif key == 'database_related_name':
            return 'corpus_viewer_items'
        elif key == 'secret_token_help':
            return None

        raise ValueError('setting-key \''+key+'\' not found')

    def add_settings_corpus(self, id_corpus, settings):
        with open(os.path.join(self.path_settings, id_corpus+'.py'), 'w') as f:
            # pprint.pprint(settings)
            content = 'DICT_SETTINGS_VIEWER = '+pprint.pformat(settings)
            f.write(content)


        self.dict_corpora[id_corpus] =  {}
        self.dict_corpora[id_corpus]['settings'] = settings
        self.dict_corpora[id_corpus]['exception'] = None
        self.update_template(id_corpus)

        self.dict_corpora[id_corpus].update(self.get_default_settings())
        
        self.update_cache()

    def get_settings_for_corpus(self, id_corpus):
        return self.dict_corpora[id_corpus]['settings']

    def get_dict_ids_to_ids_internal(self, id_corpus):
        path_corpus = os.path.join(self.path_cache, id_corpus)
        result = {}
        with open(os.path.join(path_corpus, id_corpus + '.ids_to_ids_internal'), 'rb') as handle_file_ids_to_ids_internal:
            result =  pickle.loads(handle_file_ids_to_ids_internal.read())

        return result

    def get_settings_content_for_corpus(self, id_corpus):
        with open(os.path.join(self.path_settings, id_corpus + '.py'), 'r') as f:
            return f.read()

    def set_settings_content_for_corpus(self, id_corpus, content):
        with open(os.path.join(self.path_settings, id_corpus + '.py'), 'w') as f:
           f.write(content)

    def reload_settings(self, id_corpus):
        file = id_corpus + '.py'
        settings = None
        
        try:
            settings = self.load_corpus_from_file(file)
            self.dict_corpora[id_corpus]['settings'] = settings
            self.dict_corpora[id_corpus]['exception'] = None
            self.update_template(id_corpus)
        except SyntaxError as err:
            self.dict_corpora[id_corpus]['exception'] = err.lineno
            self.dict_corpora[id_corpus]['settings'] = {}

        return settings
        
    def check_for_new_corpora(self):
        dict_tmp = {}

        # if len(self.get_corpora_with_exceptions()) > 0:
        for file in os.listdir(self.path_settings):
            id_corpus = file[:-3]

            try:
                dict_tmp[id_corpus] = self.dict_corpora[id_corpus]
            except KeyError:
                dict_tmp[id_corpus] = self.get_default_settings()
                self.dict_corpora[id_corpus] = dict_tmp[id_corpus]

            try:
                dict_tmp[id_corpus]['settings'] = self.load_corpus_from_file(file)
                self.dict_corpora[id_corpus]['settings'] = dict_tmp[id_corpus]['settings']
                dict_tmp[id_corpus]['exception'] = None
                self.dict_corpora[id_corpus]['exception'] = dict_tmp[id_corpus]['exception']
                self.update_template(id_corpus)
            except SyntaxError as err:
                dict_tmp[id_corpus]['exception'] = err.lineno
                dict_tmp[id_corpus]['settings'] = {}
        # else:
        #     for file in os.listdir(self.path_settings):
        #         id_corpus = file[:-3]

        #         try:
        #             dict_tmp[id_corpus] = self.dict_corpora[id_corpus]
        #         except KeyError:
        #             dict_tmp[id_corpus] = self.get_default_settings()
        #             try:
        #                 dict_tmp[id_corpus]['settings'] = self.load_corpus_from_file(file)
        #             except SyntaxError:
        #                 self.dict_corpora[id_corpus]['exception'] = traceback.format_exc(chain=False)

        

        self.dict_corpora = dict_tmp

        for id_corpus, value in self.dict_corpora.items():
            print(value.keys())

        self.update_cache()

    def get_corpora_with_exceptions(self):
        list_ids_corpora = [id_corpus for id_corpus in self.dict_corpora.keys() if self.dict_corpora[id_corpus]['exception'] != None]
        dict_corpora_with_exceptions = {}
        
        for id_corpus in list_ids_corpora:
            dict_corpora_with_exceptions[id_corpus] = self.dict_corpora[id_corpus]['exception']

        return dict_corpora_with_exceptions
    # delete internal format of corpus
    def delete_cache_for_corpus(self, id_corpus):
        path_corpus = os.path.join(self.path_cache, id_corpus)
        try:
            shutil.rmtree(path_corpus)
        except PermissionError:
            print('PERMISSION ERROR ON CACHE DELETION')
        except FileNotFoundError:
            print('Directory not found, probably a database corpus') 

    def delete_index_for_corpus(self, id_corpus):
        # delete index 
        try:
            self.dict_corpora[id_corpus]['handle_index'].delete()
        except KeyError:
            print('corpus was not loaded')
        except PermissionError:
            print('PERMISSION ERROR ON INDEX DELETION')

    def delete_corpus(self, id_corpus, keep_settings_file=True):
        # def handleRemoveReadonly(func, path, exc):
        #     excvalue = exc[1]
        #     if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        #         os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        #         func(path)
        #     else:
        #         raise
            # shutil.rmtree(path_corpus, ignore_errors=False, onerror=handleRemoveReadonly)

        self.delete_cache_for_corpus(id_corpus)

        self.delete_index_for_corpus(id_corpus)

        # delete data from cache
        del self.dict_corpora[id_corpus]
        self.update_cache()

        if not keep_settings_file:
            # remove/backup settings file
            file = id_corpus + '.py'
            path_settings = os.path.join(self.path_settings, file)
            path_settings_destination = os.path.join(self.path_backup, file)
            shutil.move(path_settings, path_settings_destination)

    def get_number_of_indexed_items(self, id_corpus):
        return self.dict_corpora[id_corpus]['size']

    def reindex_corpus(self, id_corpus, class_handle_index):
        settings_corpus = self.get_settings_for_corpus(id_corpus)
        self.index_corpus(id_corpus, settings_corpus, class_handle_index)

    def get_handle_index(self, id_corpus):
        return self.dict_corpora[id_corpus]['handle_index']

    def index_corpus(self, id_corpus, settings_corpus, class_handle_index):
        start_total = time.perf_counter()
        if self.debug == True:
            print('indexing \''+id_corpus+'\'')

        field_id = settings_corpus['id']

        self.dict_corpora[id_corpus]['state_loaded'] = self.State_Loaded.LOADING
        self.dict_corpora[id_corpus]['size'] = 0
        self.dict_corpora[id_corpus]['size_in_bytes'] = 0

        if class_handle_index:
            handle_index = getattr(dict_handle_indices[class_handle_index], class_handle_index)(id_corpus, settings_corpus)
            self.dict_corpora[id_corpus]['handle_index'] = handle_index
            self.dict_corpora[id_corpus]['class_handle_index'] = class_handle_index
            self.update_cache()
        else:
            handle_index = self.dict_corpora[id_corpus]['handle_index']

        handle_index.clear()
        
        handle_index.start()
        path_corpus = os.path.join(self.path_cache, id_corpus)
        if not os.path.exists(path_corpus):
            os.mkdir(path_corpus)

        error_happended = False
        with open(os.path.join(path_corpus, id_corpus + '.data'), 'wb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'wb') as handle_file_metadata:
                dict_ids_to_ids_internal = {}
                obj_handle_item = Handle_Item_Add(self.struct, handle_file_data, handle_file_metadata, self.dict_corpora[id_corpus], field_id, settings_corpus['data_fields'], dict_ids_to_ids_internal)
                start = time.perf_counter()
                try:
                    settings_corpus['load_data_function'](obj_handle_item)
                except Exception as e:
                    error_happended = True
                    # self.dict_corpora[id_corpus]['exception'] = e.lineno or 'test'
                    # self.dict_corpora[id_corpus]['exception'] = traceback.tb_lineno
                    self.dict_corpora[id_corpus]['exception'] = traceback.format_exc(chain=False)

                    if self.debug == True:
                        print(self.dict_corpora[id_corpus]['exception'])

                    # self.delete_corpus(id_corpus, False)
                    self.delete_cache_for_corpus(id_corpus)
                    self.delete_index_for_corpus(id_corpus)

                    self.dict_corpora[id_corpus]['state_loaded'] = self.State_Loaded.NOT_LOADED
                    self.update_cache()

                self.dict_corpora[id_corpus]['state_loaded'] = self.State_Loaded.NOT_LOADED

                with open(os.path.join(path_corpus, id_corpus + '.ids_to_ids_internal'), 'wb') as handle_file_ids_to_ids_internal:
                    handle_file_ids_to_ids_internal.write(pickle.dumps(dict_ids_to_ids_internal))

                indexing_only = round(float(time.perf_counter()-start_total) * 1000, 2)

        if not error_happended:
            handle_index.finish()

            print('size of corpus: '+str(self.dict_corpora[id_corpus]['size']))
            print('size of corpus (bytes): '+str(self.dict_corpora[id_corpus]['size_in_bytes']))
            print('')
            self.dict_corpora[id_corpus]['state_loaded'] = self.State_Loaded.LOADED
            self.update_cache()

            if self.debug == True:
                print('writing time: '+str(round(float(time.perf_counter()-start_total) * 1000, 2))+'ms')
                print('indexing only: '+str(indexing_only)+'ms')

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

    def get_items(self, id_corpus, list_indices):       
        path_corpus = os.path.join(self.path_cache, id_corpus)

        with open(os.path.join(path_corpus, id_corpus + '.data'), 'rb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'rb') as handle_file_metadata:
                obj_handle_item = Handle_Item_Get_Item(self.struct, self.length_struct, handle_file_data, handle_file_metadata)
                return obj_handle_item.get_items(list_indices)

    def get_item(self, id_corpus, id_item):       
        path_corpus = os.path.join(self.path_cache, id_corpus)

        with open(os.path.join(path_corpus, id_corpus + '.data'), 'rb') as handle_file_data:
            with open(os.path.join(path_corpus, id_corpus + '.metadata'), 'rb') as handle_file_metadata:
                obj_handle_item = Handle_Item_Get_Item(self.struct, self.length_struct, handle_file_data, handle_file_metadata)
                return obj_handle_item.get_item(id_item)

    def get_active_handle_indices(self):
        list_handle_indices = []

        for key in sorted(dict_handle_indices.keys()):
            class_obj_handle_index = getattr(dict_handle_indices[key], key)
            if class_obj_handle_index.is_active():
                dict_handle_index = {}
                dict_handle_index['key'] = key            
                dict_handle_index['name'] = class_obj_handle_index.get_display_name()           
                list_handle_indices.append(dict_handle_index)

        return list_handle_indices

    def get_state_loaded(self, id_corpus):       
        if self.get_setting_for_corpus('data_type', id_corpus) == 'database':
            return self.State_Loaded.LOADED

        return self.dict_corpora[id_corpus]['state_loaded']

    @unique
    class State_Loaded(IntEnum):
        LOADED = 0
        NOT_LOADED = 1
        LOADING = 2
    
from django.core.cache import cache
from .Item_Handle import *
import time
import os

class Data_Manager:
   def __init__(self, glob_settings):
      self.debug = True
      self.path_cache = '../cache'

      self.dict_data = self.init_data()

   def init_data(self):
      dict_data = cache.get('metadata_corpora')
      if(dict_data == None):
         dict_data = {}

      return dict_data

   def index_corpus(self, id_corpus, corpus):

      field_id = corpus['id']

      dict_data = {}
      dict_data['is_loaded'] = False
      dict_data['size'] = 0
      dict_data['size_in_bytes'] = 0
      dict_data['list'] = []

      self.dict_data[id_corpus] = dict_data


      with open(os.path.join(self.path_cache, id_corpus + '.pickle'), 'wb') as handle_file_data:
         with open(os.path.join(self.path_cache, id_corpus + '_metadata.pickle'), 'wb') as handle_file_metadata:
            start = time.perf_counter()
            item_handle = Item_Handle(dict_data, id_corpus, handle_file_data, handle_file_metadata, field_id)

            corpus['load_data_function'](item_handle)
            print('writing time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

      # cache.set('metadata_corpora', glob_cache)

      print('size of corpus: '+str(dict_data['size']))
      print('size of corpus (bytes): '+str(dict_data['size_in_bytes']))
      print('')

      with open(os.path.join(self.path_cache, id_corpus + '_metadata.pickle'), 'rb') as handle_file_metadata:
         start = time.perf_counter()
         item_handle = Item_Handle(dict_data, id_corpus, None, handle_file_metadata, field_id)

         for index, item in enumerate(dict_data['list']):
            item_handle.get(index)
         print('loading time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

      dict_data['is_loaded'] = True
      # print(dict_data)
      return dict_data

   def get_all_ids_for_corpus(self, id_corpus, corpus):
      if self.debug == True:
         print('loading all ids from \''+id_corpus+'\'')

      try:
         return self.dict_data[id_corpus]['list']
      except KeyError:
         return self.index_corpus(id_corpus, corpus)['list']
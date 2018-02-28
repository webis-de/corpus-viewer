from .Handle_Index import * 
from whoosh.index import create_in, open_dir, exists_in
from whoosh.query import Term, Phrase
from whoosh.collectors import Collector
from whoosh.scoring import WeightingModel, BaseScorer
from whoosh.analysis import StemmingAnalyzer, RegexTokenizer, LowercaseFilter, NgramFilter
# from whoosh.qparser import QueryParser
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC, BOOLEAN, ID
from django.conf import settings
import os
import time
import shutil

class Handle_Index_Whoosh(Handle_Index):
    def __init__(self, id_corpus, settings_corpus):
        Handle_Index.__init__(self, id_corpus, settings_corpus)
        self.path_index = os.path.join(settings.PATH_FILES_INDEX, id_corpus)
        self.field_internal_id = 'viewer__id'

        self.suffix_case_sensitive = '_cs'
        self.suffix_case_insensitive = '_ci'

        analyzer_whitespace = RegexTokenizer()
        analyzer_whitespace_lowercase = analyzer_whitespace | LowercaseFilter()

        self.analyzer_string_case_sensitive = analyzer_whitespace
        self.analyzer_string_case_insensitive = analyzer_whitespace_lowercase

        self.analyzer_text_case_sensitive = analyzer_whitespace
        self.analyzer_text_case_insensitive = analyzer_whitespace_lowercase

        if not os.path.exists(self.path_index):
            os.makedirs(self.path_index)

        dict_fields = {}

        for key, value in settings_corpus['data_fields'].items():
            type_data_field = value['type']
            if type_data_field == 'string':
                dict_fields[key + self.suffix_case_sensitive] = TEXT(analyzer=self.analyzer_string_case_sensitive)
                dict_fields[key + self.suffix_case_insensitive] = TEXT(analyzer=self.analyzer_string_case_insensitive)
            elif type_data_field == 'text':
                dict_fields[key + self.suffix_case_sensitive] = TEXT(analyzer=self.analyzer_text_case_sensitive)
                dict_fields[key + self.suffix_case_insensitive] = TEXT(analyzer=self.analyzer_text_case_insensitive)
            elif type_data_field == 'number':
                dict_fields[key] = NUMERIC(float, 64)
            elif type_data_field == 'boolean':
                dict_fields[key] = BOOLEAN()

        dict_fields[self.field_internal_id] = NUMERIC(stored=True)

        self.schema = Schema(**dict_fields)

        if exists_in(self.path_index) == True:
            self.ix = open_dir(self.path_index)
        else:
            self.ix = create_in(self.path_index, self.schema)

    def is_active():
        return True

    def get_display_name():
        return 'Whoosh'

    def get_description():
        return 'test html'

    def start(self):
        self.writer = self.ix.writer(limitmb=512, procs=4, multisegment=True)
        pass

    def add_item(self, id_intern, item):
        dict_data_fields = self.settings_corpus['data_fields']

        dict_document = {}
        for key, value in dict_data_fields.items():
            type_data_field = value['type']
            if type_data_field == 'number':
                dict_document[key] = item[key]                
            elif type_data_field == 'boolean':
                dict_document[key] = item[key]                
            else:
                dict_document[key + self.suffix_case_sensitive] = item[key]                
                dict_document[key + self.suffix_case_insensitive] = item[key]                
        
        dict_document[self.field_internal_id] = id_intern

        self.writer.add_document(**dict_document)

        return True

    def finish(self):
        self.writer.commit()
        pass

    def delete(self):
        shutil.rmtree(self.path_index)

    def add_string(self, data_field, value, id_intern):
        return []

    def add_text(self, data_field, value, id_intern):
        return []

    def add_number(self, data_field, value, id_intern):
        return []


    def get_boolean(self, data_field, value):
        print('Booelan: searching for \'{}\' in \'{}\''.format(value, data_field))
        with self.ix.searcher(weighting=CustomWeightingModel) as searcher:
            # for name in self.schema.names():
            #     print('')
            #     print(name)
            #     print(list(searcher.lexicon(name)))
            #     print('')

            query = query = Term(data_field, value)
            # print(query)
            # print(tokens)
            results = searcher.search(query, limit=None, sortedby=None)
            # print(len(results))
            # for result in results:
            #     print(result)
            return [result[self.field_internal_id] for result in results]

    def get_string(self, data_field, value, is_case_insensitive):
        print('STRING: searching for \'{}\' in \'{}\''.format(value, data_field))
        with self.ix.searcher(weighting=CustomWeightingModel) as searcher:
            # for name in self.schema.names():
            #     print('')
            #     print(name)
            #     print(list(searcher.lexicon(name)))
            #     print('')

            if is_case_insensitive == True:
                tokens = [token.text for token in self.analyzer_string_case_insensitive(value)]
                query = Phrase(data_field + self.suffix_case_insensitive, tokens)
            else:
                tokens = [token.text for token in self.analyzer_string_case_sensitive(value)]
                query = Phrase(data_field + self.suffix_case_sensitive, tokens)
            print(tokens)
            results = searcher.search(query, limit=None, sortedby=None)
            print(len(results))
            # for result in results:
            #     print(result)
            return [result[self.field_internal_id] for result in results]

    def get_text(self, data_field, value, is_case_insensitive):
        print('TEXT: searching for \'{}\' in \'{}\''.format(value, data_field))
        with self.ix.searcher(weighting=CustomWeightingModel) as searcher:
            if is_case_insensitive == True:
                tokens = [token.text for token in self.analyzer_text_case_insensitive(value)]
                query = Phrase(data_field + self.suffix_case_insensitive, tokens)
            else:
                tokens = [token.text for token in self.analyzer_text_case_sensitive(value)]
                query = Phrase(data_field + self.suffix_case_sensitive, tokens)
            
            collector = CustomCollector()

            start = time.perf_counter()
            searcher.search_with_collector(query, collector)
            print('real searching time: '+str(round(float(time.perf_counter()-start) * 1000, 2))+'ms')

            return collector.results

    def get_number(self, data_field, value):
        print('NUMBER: searching for \'{}\' in \'{}\''.format(value, data_field))
        with self.ix.searcher(weighting=CustomWeightingModel) as searcher:
            query = Term(data_field, value)
            results = searcher.search(query, limit=None, sortedby=None)
            
            return [result[self.field_internal_id] for result in results]

    def clear(self):
        create_in(self.path_index, self.schema)

class CustomCollector(Collector):
    def prepare(self, top_searcher, q, context):
        # Always call super method in prepare
        Collector.prepare(self, top_searcher, q, context)
        self.results = []
        self.internal_field = 'viewer__id'

    def collect(self, sub_docnum):
        self.results.append(self.top_searcher.stored_fields(self.offset + sub_docnum)[self.internal_field])

class CustomWeightingModel(WeightingModel):
    def scorer(self, searcher, fieldname, text, qf=1):
        return CustomWeightingModelScorer()

class CustomWeightingModelScorer(BaseScorer):
    def score(self, matcher):
        return 0.0
from .Handle_Index import * 
from whoosh.index import create_in, open_dir, exists_in
from whoosh.query import Term, Phrase
from whoosh.analysis import StemmingAnalyzer, RegexTokenizer
# from whoosh.qparser import QueryParser
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC, ID
import os


class Handle_Index_Whoosh(Handle_Index):
    def __init__(self, id_corpus, settings_corpus):
        Handle_Index.__init__(self, id_corpus, settings_corpus)
        self.path_index = os.path.join('../index_whoosh', id_corpus)
        self.field_internal_id = 'viewer__id'

        self.suffix_case_sensitive = '_cs'
        self.suffix_case_insensitive = '_ci'

        self.analyzer_string_case_sensitive = StemmingAnalyzer()
        self.analyzer_string_case_insensitive = StemmingAnalyzer()

        self.analyzer_text_case_sensitive = StemmingAnalyzer()
        self.analyzer_text_case_insensitive = StemmingAnalyzer()

        self.analyzer_number_case_insensitive = StemmingAnalyzer()

        if not os.path.exists(self.path_index):
            os.makedirs(self.path_index)

        print('CREATE INDEX')
        dict_fields = {}

        for key, value in settings_corpus['data_fields'].items():
            type_data_field = value['type']
            if type_data_field == 'string':
                dict_fields[key + self.suffix_case_sensitive] = ID(analyzer=self.analyzer_string_case_sensitive)
                dict_fields[key + self.suffix_case_insensitive] = ID(analyzer=self.analyzer_string_case_insensitive)
            elif type_data_field == 'text':
                dict_fields[key + self.suffix_case_sensitive] = TEXT(analyzer=self.analyzer_text_case_sensitive)
                dict_fields[key + self.suffix_case_insensitive] = TEXT(analyzer=self.analyzer_text_case_insensitive)
            elif type_data_field == 'number':
                dict_fields[key] = TEXT(analyzer=self.analyzer_number_case_insensitive)

        dict_fields[self.field_internal_id] = NUMERIC(stored=True)

        self.schema = Schema(**dict_fields)

        if exists_in(self.path_index) == True:
            self.ix = open_dir(self.path_index)
        else:
            self.ix = create_in(self.path_index, self.schema)

    def start(self):
        self.writer = self.ix.writer()
        pass

    def add_item(self, id_intern, item):
        item[self.field_internal_id] = id_intern

        self.writer.add_document(**item)
        return True

    def finish(self):
        self.writer.commit()
        pass

    def add_string(self, data_field, value, id_intern):
        return []

    def add_text(self, data_field, value, id_intern):
        return []

    def add_number(self, data_field, value, id_intern):
        return []


    def get_string(self, data_field, value, case_sensitive):
        print('STRING: searching for \'{}\' in \'{}\''.format(value, data_field))
        with self.ix.searcher() as searcher:
            # for foo in self.settings_corpus['data_fields'].keys():
            #     print(list(searcher.lexicon(foo)))

            query = Term(data_field, value)
            results = searcher.search(query, limit=None)
            print(len(results))
            # for result in results:
            #     print(result)
            return [result[self.field_internal_id] for result in results]

    def get_text(self, data_field, value, case_sensitive):
        print('TEXT: searching for \'{}\' in \'{}\''.format(value, data_field))
        with self.ix.searcher() as searcher:
            tokenizer = StemmingAnalyzer()
            tokens = [token.text for token in tokenizer(value)]
            query = Phrase(data_field, tokens)
            results = searcher.search(query, limit=None)
            print(len(results))
            # for result in results:
            #     print(result)
            return [result[self.field_internal_id] for result in results]

    def get_number(self, data_field, value):
        return []

    def clear(self):
        create_in(self.path_index, self.schema)

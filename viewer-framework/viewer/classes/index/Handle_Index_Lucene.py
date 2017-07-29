from .Handle_Index import * 

class Handle_Index_Lucene(Handle_Index):
    def __init__(self, id_corpus):
        self.id_corpus = id_corpus
        
    def is_active():
        return False

    def get_display_name():
        return 'Lucene'

    def get_description():
        return 'test html'
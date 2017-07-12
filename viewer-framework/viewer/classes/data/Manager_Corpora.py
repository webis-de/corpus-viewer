import os 
import shutil

class Manager_Corpora:
    def __init__(self):
        self.debug = True
        self.path_settings = '../settings'
        self.path_backup = 'backup_settings'
        self.dict_corpora = self.init_data()

    def init_data(self):
        dict_corpora = {}

        if not os.path.exists(self.path_settings):
            os.mkdir(self.path_settings)

        if not os.path.exists(self.path_backup):
            os.mkdir(self.path_backup)

        for file in os.listdir(self.path_settings):
            dict_corpora[file[:-3]] = self.load_corpus_from_file(file)

        return dict_corpora

    def corpus_exists(self, id_corpus):
        return id_corpus in self.dict_corpora

    def delete_corpus(self, id_corpus):
        file = id_corpus + '.py'
        path_settings = os.path.join(self.path_settings, file)
        path_settings_destination = os.path.join(self.path_backup, file)
        shutil.move(path_settings, path_settings_destination)

        del self.dict_corpora[id_corpus]

    def load_corpus_from_file(self, file):
        with open(os.path.join(self.path_settings, file), 'r') as f:
            compiled = compile(f.read(), '<string>', 'exec')
            global_env = {}
            local_env = {}
            exec(compiled, global_env, local_env)

            if self.debug == True:
                print('parsed settings for \'{}\''.format(file))

        return local_env['DICT_SETTINGS_VIEWER']

    def check_for_new_corpora(self):
        dict_tmp = {}

        for file in os.listdir(self.path_settings):
            id_corpus = file[:-3]

            try:
                dict_tmp[id_corpus] = self.dict_corpora[id_corpus]
            except KeyError:
                dict_tmp[id_corpus] = self.load_corpus_from_file(file)

        self.dict_corpora = dict_tmp

    def get_ids_corpora(self, sorted_by=None):
        if sorted_by == None:
            return self.dict_corpora.keys()
        elif sorted_by == 'name':
            return sorted(self.dict_corpora.keys(), key=lambda id_corpus: self.dict_corpora[id_corpus]['name'])

    def set_current_corpus(self, request):
        default = list(self.dict_corpora.keys())[0]
        key = 'viewer__current_corpus'
        sessionkey = 'viewer__' + key

        if request.GET.get(key) != None:
            request.session[sessionkey] = request.GET.get(key)
        else:
            if sessionkey not in request.session:
                request.session[sessionkey] = default

    def reload_settings(self, id_corpus):
        file = id_corpus + '.py'
        settings = self.load_corpus_from_file(file)
        self.dict_corpora[id_corpus] = settings
        return settings

    def get_settings_for_corpus(self, id_corpus):
        return self.dict_corpora[id_corpus]

    def get_setting_for_corpus(self, key, id_corpus):
        settings_corpus = self.dict_corpora[id_corpus]
        if key in settings_corpus:
            return settings_corpus[key]

        if key == 'use_cache':
            return False;
        elif key == 'page_size':
            return 25;

        raise ValueError('setting-key \''+key+'\' not found')

    # def get_setting_for_corpus(id_corpus, key = None):
    #     return glob_settings[id_corpus][key]
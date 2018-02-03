class MainRouter:
    """
    A router to control all database operations on models in the
    auth application.
    """
    def db_for_read(self, model, **hints):
        # print('########### db_for_read')
        # print(model._meta.app_label)
        if model._meta.app_label.startswith('corpus_viewer_'):
            return model._meta.app_label
        else:
            return None

        # list_model_name = model.__name__.split('@')
        # if len(list_model_name) == 2:
        #     return list_model_name[0]

        # return None

    def db_for_write(self, model, **hints):
        # print('########### db_for_write')
        # print(model._meta.app_label)
        if model._meta.app_label.startswith('corpus_viewer_'):
            return model._meta.app_label
        else:
            return None

        # list_model_name = model.__name__.split('@')
        # if len(list_model_name) == 2:
        #     return list_model_name[0]

        # return None

    def allow_relation(self, obj1, obj2, **hints):
        # print('########### allow_relation')
        # print(obj1._meta.app_label)
        # print(obj2._meta.app_label)
        if obj1._meta.app_label == obj2._meta.app_label or obj1._meta.app_label == 'viewer' or obj2._meta.app_label == 'viewer':
            # print('yes') 
            return True
        else:
            # print('no')
            return False

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # print('########### allow_migrate')
        # print(app_label)
        # print(db)
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if app_label.startswith('corpus_viewer_'):
            if db == app_label:
                return True
            else:
                return False

        if db.startswith('corpus_viewer_'):
            if not app_label.startswith('corpus_viewer_'):
                return False


        return None
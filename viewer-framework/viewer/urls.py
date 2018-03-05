from django.urls import path

from . import views

app_name = 'viewer'
urlpatterns = [
    path('<str:id_corpus>', views.index, name='index'),
    path('<str:id_corpus>/<int:id_internal_item>', views.view_item, name='view_item'),
    path('<str:id_corpus>/get_page', views.get_page, name='get_page'),
    path('<str:id_corpus>/tags/export', views.tags_export, name='tags_export'),
    path('<str:id_corpus>/tags', views.tags, name='tags'),
    path('<str:id_corpus>/enter_token', views.add_token, name='add_token'),
    path('<str:id_corpus>/edit', views.edit, name='edit'),

    # API calls
    path('api/add_corpus', views.api_add_corpus, name='api_add_corpus'),
    path('api/refresh_corpora', views.api_refresh_corpora, name='api_refresh_corpora'),
    path('api/delete_corpus', views.api_delete_corpus, name='api_delete_corpus'),
]
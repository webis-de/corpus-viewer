from django.conf.urls import url

from . import views

app_name = 'viewer'
urlpatterns = [
    url(r'^(?P<id_corpus>[^\/]+)$', views.index, name='index'),
    url(r'^(?P<id_corpus>[^\/]+)/(?P<id_internal_item>[0-9]+)/$', views.view_item, name='view_item'),
    url(r'^(?P<id_corpus>[^\/]+)/get_page$', views.get_page, name='get_page'),
    url(r'^(?P<id_corpus>[^\/]+)/tags$', views.tags, name='tags'),
    url(r'^(?P<id_corpus>[^\/]+)/enter_token$', views.add_token, name='add_token'),
]
from django.conf.urls import url

from . import views

app_name = 'viewer'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_page$', views.get_page, name='get_page'),
    url(r'^tags$', views.tags, name='tags'),
    url(r'^documentation$', views.documentation, name='documentation'),
    url(r'^delete_session$', views.delete_session, name='delete_session'),
]
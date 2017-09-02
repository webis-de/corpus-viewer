from django.conf.urls import url

from . import views

app_name = 'dashboard'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^documentation$', views.documentation, name='documentation'),
    url(r'^delete_session$', views.delete_session, name='delete_session'),
]
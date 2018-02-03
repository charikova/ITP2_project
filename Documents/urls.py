from django.conf.urls import url
from . import views
from BookRequests import views as requests_views
from Documents.models import *

urlpatterns = [
    #main page
    url(r'^$', views.IndexView.as_view(), name='index'),
    #user stuff
    url(r'^(?P<pk>\d+)/$', views.document_detail, name='document_detail'),
    #librarian stuff
    url(r'^(?P<pk>\d+)/update/$', views.update_doc, name='update_doc'),
    url(r'^(?P<pk>\d+)/delete/$', views.del_doc, name='del_doc'),
    url(r'^create/$', views.create_doc, name='create_doc'),
    url(r'^add_doc/$', views.add_doc, name='add_doc'),

]

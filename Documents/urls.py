from django.conf.urls import url
from . import views
from innopolka import settings
from django import views as django_views

urlpatterns = [
    # main page
    url(r'^$', views.IndexView.as_view(), name='index'),
    # user stuff
    url(r'^(?P<pk>\d+)/$', views.document_detail, name='document_detail'),
    # librarian stuff
    url(r'^(?P<pk>\d+)/update/$', views.update_doc, name='update_doc'),
    url(r'^(?P<pk>\d+)/delete/$', views.del_doc, name='del_doc'),
    url(r'^create/$', views.create_doc, name='create_doc'),
    url(r'^add_doc/$', views.add_doc, name='add_doc'),
    url(r'^checked_out_docs/$', views.CheckedOutDocsView.as_view(), name='checked_out_docs'),
    url(r'(?:.*?/)?(?P<path>(images)/.+)$', django_views.static.serve, {'document_root': settings.STATIC_ROOT}),

]

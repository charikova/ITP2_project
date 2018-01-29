from django.conf.urls import url
from . import views
from Documents.models import *

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    #documents/<doc_id>
    url(r'^(?P<pk>\d+)/$', views.document_detail, name='document_detail'),
    url(r'^(?P<pk>\d+)/checkout/$', views.checkout, name='checkout'),
    #librarian stuff
    url(r'^(?P<pk>\d+)/update/$', views.update_doc, name='update_doc'),
    url(r'^(?P<pk>\d+)/delete/$', views.DeleteDocument.as_view(), name='delete_doc'),
    url(r'^add_doc/$', views.add_doc, name='add_doc'),

    *[url(r'^create/{}/$'.format(cls.type), views.CreateDocument.as_view(model=cls))
      for cls in Document.__subclasses__()[:-1]],

]

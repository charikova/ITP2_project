from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    #documents/<doc_id>
    url(r'^(?P<pk>\d+)/$', views.DocumentDetail.as_view(), name='document_detail'),
    #librarian stuff
    url(r'^(?P<pk>\d+)/update/$', views.UpdateDocument.as_view(), name='update_doc'),
    url(r'^(?P<pk>\d+)/delete/$', views.DeleteDocument.as_view(), name='delete_doc'),
    url(r'^create/', views.CreateDocument.as_view(), name='create_doc'),
    url(r'^(?P<pk>\d+)/checkout/$', views.checkout, name='checkout'),
]

from django.conf.urls import url
from . import views

urlpatterns = [
<<<<<<< HEAD
    url(r'^$', views.index, name='index'),
    #documents/<doc_id>
    url(r'^(\d+)/$', views.show_doc_inf, name='show_doc_inf'),


=======
    url(r'^$', views.IndexView.as_view(), name='index'),
    #documents/<doc_id>
    url(r'^(?P<pk>\d+)/$', views.DocumentDetail.as_view(), name='document_detail'),
>>>>>>> dev
]

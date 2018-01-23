from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    #documents/<doc_id>
    url(r'^(?P<pk>\d+)/$', views.DocumentDetail.as_view(), name='document_detail'),
]

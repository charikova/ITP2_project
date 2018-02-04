from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.RequestsView.as_view(), name='requests'),
    url(r'^make_new/$', views.make_new, name='make_new'),
    url(r'^approve/$', views.approve_request, name='approve_request'),
    url(r'^takebook/', views.takebook, name='takebook'),
    url(r'^refuse/', views.refuse, name='refuse'),
]


from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', views.login, name='login'),
    url(r"^$", views.index, name='index'),
    url(r'^make_user/$', views.make_user, name='make_user'),
    url(r'^identify_user/$', views.identify_user, name='identify_user'),
    url(r'^return_copies/$', views.return_copies, name='return_copies'),
]
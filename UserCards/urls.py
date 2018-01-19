from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^signup$/', views.signup, name='signup'),
    url(r"^$", views.index, name='index'),
    url(r'^make_user/$', views.make_user, name='make_user'),
]
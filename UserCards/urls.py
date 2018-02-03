from django.conf.urls import url
from . import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    url(r'^$', views.user_card_info, name='user_card_info'),
    url(r'^login/$', login, {'template_name': 'UserCards/login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': '/user/login/'}, name='logout'),
    url(r'^edit/$', views.EditCardView.as_view(), name='edit'),
    url(r'^return_copies/$', views.return_copies, name='return_copies'),
    url(r'^bookrequests/(?P<pk>[0-9]+)/$', views.booktaker_view, name='booktaker_view'),
    url(r'^bookrequests/$', views.BookRequestsView.as_view(), name='bookrequests'),
    url(r'^bookrequests/(?P<pk>[0-9]+)/(?P<booktaker>[0-9]+)/$', views.givebook, name='givebook'),
    url(r'^bookrequests/(?P<pk>[0-9]+)/takebook/(?P<user>[0-9]+)/(?P<copy>[0-9]+)$', views.takebook, name='takebook'),
]



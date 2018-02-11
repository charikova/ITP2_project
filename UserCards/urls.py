from django.conf.urls import url
from . import views
from django.contrib.auth.views import login, logout


urlpatterns = [
    url(r'^create_user/$', views.CreateUserView.as_view(), name='create_user'),
    url(r'^$', views.user_card_info, name='user_card_info'),
    url(r'^all/$', views.AllUsersView.as_view(), name='all_users'),
    url(r'^login/$', login, {'template_name': 'UserCards/login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': '/user/login/'}, name='logout'),
    url(r'^edit/$', views.EditCardView.as_view(), name='edit'),
    url(r'^list/$', views.AllUsersView.as_view(), name='list'),

]

from django.conf.urls import url
from . import views
from django.contrib.auth.views import login, logout
import Documents


urlpatterns = [
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    #url(r'^$', views.SignupView.as_view(), name='signup'),
    url(r'^login/$', login, {'template_name': 'UserCards/login.html'}, name='login'),
    url(r'^logout/$', logout, {'next_page': '/user/login/'}, name='logout'),

]


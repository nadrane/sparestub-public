# Django modules
from django.conf.urls import patterns, url

from .views import signup, login, logout

urlpatterns = patterns('',
                       url(r'signup/$', signup, name='submit'),
                       #url(r'basic_info/$', views.basic_info),
                       url(r'login/$', login, name='login'),
                       url(r'logout/$', logout, name='logout')
                       )
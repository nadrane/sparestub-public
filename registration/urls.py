# Django Imports
from django.conf.urls import patterns, url

# SpareStub Imports
from .views import signup, login, logout, login_redirect

urlpatterns = patterns('',
                       url(r'signup/$', signup, name='submit'),
                       #url(r'basic_info/$', views.basic_info),
                       url(r'login/$', login, name='login'),
                       url(r'login_redirect/$', login_redirect, name='login_redirect'),
                       url(r'logout/$', logout, name='logout'),
                       )
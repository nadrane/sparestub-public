# Django Imports
from django.conf.urls import patterns, url

# SpareStub Imports
from .views import signup, login, logout, login_redirect, create_forgot_password, reset_password

urlpatterns = patterns('',
                       url(r'signup/$', signup, name='submit'),
                       #url(r'basic_info/$', views.basic_info),
                       url(r'login/$', login, name='login'),
                       url(r'login_redirect/$', login_redirect, name='login_redirect'),
                       url(r'logout/$', logout, name='logout'),
                       url(r'create_forgot_password/$', create_forgot_password, name='create_forgot_password'),
                       url(r'reset_password/(?P<reset_link>[.]20)/$', reset_password, name='reset_password'),

                       )
# Django Imports
from django.conf.urls import patterns, url

# SpareStub Imports
from .views import signup, login, logout, login_redirect, create_forgot_password, reset_password,\
    create_email_confirmation_link, confirm_email

urlpatterns = patterns('',
                       url(r'signup/$', signup, name='submit'),
                       url(r'login/$', login, name='login'),
                       url(r'login_redirect/$', login_redirect, name='login_redirect'),
                       url(r'logout/$', logout, name='logout'),
                       url(r'create_forgot_password/$', create_forgot_password, name='create_forgot_password'),
                       url(r'reset_password/(?P<reset_link>[a-zA-Z0-9]{50})/$', reset_password, name='reset_password'),
                       url(r'create_confirm_email/$', create_email_confirmation_link,
                           name='create_email_confirmation_link'),
                       url(r'confirm_email/(?P<confirm_link>[a-zA-Z0-9]{50})/$', confirm_email, name='confirm_email'),
                       )
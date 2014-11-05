__author__ = 'nicholasdrane'

# Django Imports
from django.conf.urls import patterns, url

# SpareStub Imports
from .views import inbox, send_message

urlpatterns = patterns('',
                       url(r'inbox/$', inbox, name='inbox'),
                       url(r'send_message/$', send_message, name='send_message'),
                       )

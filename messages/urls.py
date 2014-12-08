__author__ = 'nicholasdrane'

# Django Imports
from django.conf.urls import patterns, url

# SpareStub Imports
from .views import inbox, send_message, message_user_modal

urlpatterns = patterns('',
                       url(r'message_user_modal/(?P<ticket_id>[0-9]+)$', message_user_modal, name='message_user_modal'),
                       url(r'inbox/$', inbox, name='inbox'),
                       url(r'send_message/$', send_message, name='send_message'),
                       )

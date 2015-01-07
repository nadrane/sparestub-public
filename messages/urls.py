# Django Imports
from django.conf.urls import patterns, url

# SpareStub Imports
from .views import inbox, send_message, message_user_modal, mark_messages_read

urlpatterns = patterns('',
                       url(r'mark_messages_read/$', mark_messages_read, name='mark_messages_read'),
                       url(r'send_message/(?P<ticket_id>[0-9]+)$', send_message, name='send_message'),
                       url(r'message_user_modal/(?P<ticket_id>[0-9]+)$', message_user_modal, name='message_user_modal'),
                       url(r'inbox/$', inbox, name='inbox'),
                       )

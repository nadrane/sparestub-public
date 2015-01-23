# Django Imports
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

# Modules Imports
from .views import inbox, send_message, MessageUserModal, mark_messages_read, messages_hidden_toggle, can_message

urlpatterns = patterns('',
                       url(r'messages_hidden_toggle/$', messages_hidden_toggle, name='messages_hidden_toggle'),
                       url(r'mark_messages_read/$', mark_messages_read, name='mark_messages_read'),
                       url(r'send_message/$', send_message, name='send_message'),
                       url(r'can_message/$', can_message, name='can_message'),
                       url(r'message_user_modal/(?P<ticket_id>[0-9]+)$',
                           login_required(MessageUserModal.as_view()),
                           name='message_user_modal'),
                       url(r'inbox/$', inbox, name='inbox'),
                       )
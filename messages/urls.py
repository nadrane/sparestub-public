# Django Imports
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required


# SpareStub Imports
from .views import inbox, send_message, MessageUserModal, mark_messages_read

urlpatterns = patterns('',
                       url(r'mark_messages_read/$', mark_messages_read, name='mark_messages_read'),
                       url(r'send_message/$', send_message, name='send_message'),
                       url(r'message_user_modal/(?P<ticket_id>[0-9]+)$',
                           login_required(MessageUserModal.as_view()),
                           name='message_user_modal'),
                       url(r'inbox/$', inbox, name='inbox'),
                       )
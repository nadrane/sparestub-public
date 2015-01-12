# Django Imports
from django.conf.urls import patterns, url
from django.contrib import admin

# Module Imports
from .views import request_to_buy, can_request_ticket

admin.autodiscover()

urlpatterns = patterns('',
                       url(r'request_to_buy/$', request_to_buy, name='request_to_buy'),
                       url(r'can_request_ticket//(?P<ticket_id>[0-9]+)$', can_request_ticket, name="can_request_ticket")
                       )
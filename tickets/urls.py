# Django Imports
from django.conf.urls import patterns, url
from django.contrib import admin

# Haystack Imports
from haystack.query import SearchQuerySet

# Module Imports
from .views import valid_ticket, submit_ticket, SearchResults, delete_ticket, can_delete_ticket
from .forms import SearchTicketForm

admin.autodiscover()

# Only include tickets that are not purchased and not deactivated. Sort them closest to event time.
sqs = SearchQuerySet().filter(status='P').order_by('start_datetime')

urlpatterns = patterns('',
                       url(r'can_delete_ticket/(?P<ticket_id>[0-9]+)$', can_delete_ticket, name='can_delete_ticket'),
                       url(r'delete_ticket/(?P<ticket_id>[0-9]+)$', delete_ticket, name='delete_ticket'),
                       url(r'submit_ticket/$', submit_ticket, name='submit_ticket'),
                       url(r'valid_ticket/$', valid_ticket, name='valid_ticket'),
                       url(r'search_ticket/$',
                           view=SearchResults(searchqueryset=sqs, form_class=SearchTicketForm),
                           name='haystack_search'),

                       )
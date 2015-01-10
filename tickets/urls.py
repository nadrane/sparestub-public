# Django Imports
from django.conf.urls import patterns, url
from django.contrib import admin

# Haystack Imports
from haystack.query import SearchQuerySet

# SpareStub Imports
from .views import submit_ticket, SearchResults, request_to_buy
from .forms import SearchTicketForm

admin.autodiscover()

# Only include tickets that are not purchased and not deactivated. Sort them closest to event time.
sqs = SearchQuerySet().filter(is_active=True).order_by('start_datetime')

urlpatterns = patterns('',
                       url(r'submit_ticket/$', submit_ticket, name='submit_ticket'),
                       url(r'search_ticket/$',
                           view=SearchResults(searchqueryset=sqs, form_class=SearchTicketForm),
                           name='haystack_search'),
                       url(r'request_to_buy/(?P<ticket_id>[0-9]+)$', request_to_buy, name='request_to_buy')
                       )
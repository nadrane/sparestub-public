# Django Imports
from django.conf.urls import patterns, url
from django.contrib import admin

# Haystack Imports
from haystack.query import SearchQuerySet

# Module Imports
from .views import submit_ticket, SearchResults
from .forms import SearchTicketForm

admin.autodiscover()

# Only include tickets that are not purchased and not deactivated. Sort them closest to event time.
sqs = SearchQuerySet().filter(is_active=True).order_by('start_datetime')

urlpatterns = patterns('',
                       url(r'submit_ticket/$', submit_ticket, name='submit_ticket'),
                       url(r'search_ticket/$',
                           view=SearchResults(searchqueryset=sqs, form_class=SearchTicketForm),
                           name='haystack_search'),

                       )
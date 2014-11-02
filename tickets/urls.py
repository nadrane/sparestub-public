# Django modules
from django.conf.urls import patterns, url, include

from .views import submit_ticket
from .search_indexes import TicketIndex

urlpatterns = patterns('',
                       url(r'submit_ticket/$', submit_ticket, name='submit_ticket'),
                       url(r'search_ticket/$', include('haystack.urls'))
                       )
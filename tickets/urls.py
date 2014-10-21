# Django modules
from django.conf.urls import patterns, url

from .views import submit_ticket

urlpatterns = patterns('',
                       url(r'submit_ticket/$', submit_ticket, name='submit_ticket'),
                       )
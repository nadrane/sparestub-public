from django.conf.urls import patterns, url

from .views import edit_profile, view_profile, profile_reviews, profile_tickets, view_ticket, update_question

urlpatterns = patterns('',
                       # Matches on any /profile/<username>
                       # where <username> can be any combination of upper and lower case letters and numbers
                       url(r'(?P<username>[a-zA-Z0-9]+)/update_question/(?P<question_id>[0-9]+)$', update_question,
                           name='update_question'),
                       url(r'(?P<username>[a-zA-Z0-9]+)/tickets/(?P<ticket_id>[0-9]+)$', view_ticket,
                           name='view_ticket'),
                       url(r'(?P<username>[a-zA-Z0-9]+)/tickets/$', profile_tickets, name='profile_tickets'),
                       url(r'(?P<username>[a-zA-Z0-9]+)/edit/$', edit_profile, name='edit_profile'),
                       url(r'(?P<username>[a-zA-Z0-9]+)/reviews/$', profile_reviews, name='profile_reviews'),
                       url(r'(?P<username>[a-zA-Z0-9]+)/$', view_profile, name='view_profile'),
                       )


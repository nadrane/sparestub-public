from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       # Matches on any /profile/<username>
                       # where <username> can be any combination of upper and lower case letters and numbers
                       url(r'(?P<username>[a-z0-9]+)/$', views.user_profile, name='user_profile'),
                       url(r'(?P<username>[a-z0-9]+)/reviews$', views.user_reviews, name='user_reviews'),
                       url(r'(?P<username>[a-z0-9]+)/tickets$', views.user_tickets, name='user_tickets'),
                       )


from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       # Matches on any /profile/<username>
                       # where <username> can be any combination of upper and lower case letters and numbers
                       url(r'(?P<current_username>[a-zA-Z0-9]+)/$', views.view_or_edit_profile),
                       )


# Django modules
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url(r'signup/$',
                           views.signup),
                       url(r'basic_info/$',
                           views.basic_info),
                       url(r'login/$',
                           views.login),
                       )
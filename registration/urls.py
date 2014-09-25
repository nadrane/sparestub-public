# Django modules
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
                       url(r'signup/$', 
                           views.signup),
                       url(r'profile.html/basic_info/$',
                           views.basic_info),
                       url(r'profile.html/settings/$',
                           views.settings),
                       url(r'login/$',
                           views.login),
                       url(r'logout/$',
                           views.logout),
                       url(r'check_duplicate_email/$',
                           views.check_duplicate_email),
                       url(r'check_duplicate_username/$',
                           views.check_duplicate_username),
                       url(r'profile.html/delete_photo/$',
                           views.delete_photo),
                      )
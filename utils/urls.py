from django.conf.urls import patterns, url

from .views import valid_username, valid_email, valid_zip_code, correct_password

urlpatterns = patterns('',
                       url(r'/valid_username/$', valid_username, name='valid_username'),
                       url(r'/valid_email/$', valid_email, name='valid_email'),
                       url(r'/valid_zip_code/$', valid_zip_code, name='valid_zip_code'),
                       url(r'/correct_password/$', correct_password, name='correct_password')
                       )




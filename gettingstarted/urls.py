from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import contact.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gettingstarted.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', contact.views.index, name='index'),
    url(r'^contact/$', contact.views.contact, name='contact'),
    url(r'^admin/', include(admin.site.urls)),

)

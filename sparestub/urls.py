from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import contact.views

urlpatterns = patterns('',
    url(r'^$', contact.views.home, name='homepage'),
    url(r'^blog/', include('zinnia.urls', namespace='zinnia')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^contact/', include('contact.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
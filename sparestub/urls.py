from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import contact.views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = patterns('',
    url(r'^$', contact.views.home, name='homepage'),
    #url(r'^blog/', include('zinnia.urls', namespace='zinnia')),
    url(r'^registration/', include('registration.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^contact/', include('contact.urls')),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


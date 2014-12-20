from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import contact.views
from django.conf import settings
from django.conf.urls.static import static

from utils.views import terms_of_service, privacy_policy, cookie_use

urlpatterns = patterns('',
    url(r'^$', contact.views.home, name='homepage'),
    url(r'^blog/', include('zinnia.urls', namespace='zinnia')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^profile/', include('user_profile.urls')),
    url(r'^registration/', include('registration.urls')),
    url(r'^contact/', include('contact.urls')),
    url(r'^tickets/', include('tickets.urls')),
    url(r'^messages/', include('messages.urls')),
    url(r'^utils/', include('utils.urls')),
    url(r'^tos/$', terms_of_service, name='tos'),
    url(r'^privacypolicy/$', privacy_policy, name='privacy policy'),
    url(r'^cookieuse/$', cookie_use, name='cookie use'),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
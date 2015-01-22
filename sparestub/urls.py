# Django Imports
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='homepage'),
    url(r'^tos/$', TemplateView.as_view(template_name="terms_of_service.html"), name='tos'),
    url(r'^privacypolicy/$', TemplateView.as_view(template_name="privacy_policy.html"), name='privacy policy'),
    url(r'^disputeresolution/$', TemplateView.as_view(template_name="dispute_resolution.html"), name='dispute resolution'),
    url(r'^buyersguide/$', TemplateView.as_view(template_name="buyers_guide.html"), name='buyers guide'),
    url(r'^sellersguide/$', TemplateView.as_view(template_name="sellers_guide.html"), name='sellers guide'),
    url(r'^safetytips/$', TemplateView.as_view(template_name="safety_tips.html"), name='safety tips'),

    url(r'^blog/', include('zinnia.urls', namespace='zinnia')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^profile/', include('user_profile.urls')),
    url(r'^registration/', include('registration.urls')),
    url(r'^contact/', include('contact.urls')),
    url(r'^tickets/', include('tickets.urls')),
    url(r'^messages/', include('messages.urls')),
    url(r'^utils/', include('utils.urls')),
    url(r'^requests/', include('asks.urls')),
    url(r'^admin/', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
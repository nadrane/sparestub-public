# Django Imports
from django.conf.urls import patterns, url

# Module Imports
from .views import customer_exists

urlpatterns = patterns('', url(r'customer_exists/$', customer_exists, name='customer_exists'))
# Standard Imports
import os
from datetime import timedelta

# 3rd Party Imports
from celery import Celery

# Django Imports
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sparestub.settings')

app = Celery('sparestub')

# Using a string here means the worker will not have to pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
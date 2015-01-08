"""
WSGI config for sparestub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import newrelic.agent
#newrelic.agent.initialize('newrelic.ini')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sparestub.settings.production")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
__author__ = 'Nick'

from .base import *
import dj_database_url

# Keep these in here always. regardless of what base.py says. Just be safe.
DEBUG = False
TEMPLATE_DEBUG = False

# Put on hold until https://github.com/cobrateam/django-htmlmin is migrated to python 3.
# Or, more likely, migrate part of the project myself.
MIDDLEWARE_CLASSES += (#'htmlmin.middleware.HTMLMinMiddleware',
                       #'htmlmin.middleware.MarkRequestMiddleware',
                       )

STATIC_URL = 'https://s3.amazonaws.com/sparestub-production/'
MEDIA_URL = ''


DATABASES['default'] = dj_database_url.config()


#ALLOWED_HOSTS = ['sparestub.com', 'www.sparestub.com']

AWS_BUCKET_NAME = 'sparestub-production'
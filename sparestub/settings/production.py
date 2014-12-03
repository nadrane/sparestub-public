__author__ = 'Nick'

from .base import *

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

#ALLOWED_HOSTS = ['sparestub.com', 'www.sparestub.com']

# File Storage Backend Settings
DEFAULT_FILE_STORAGE = 'utils.backends.s3_boto.S3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'sparestub-production'
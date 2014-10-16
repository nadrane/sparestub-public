__author__ = 'Nick'

from .base import *

# Keep these in here always. regardless of what base.py says. Just be safe.
DEBUG = True
TEMPLATE_DEBUG = False

# Put on hold until https://github.com/cobrateam/django-htmlmin is migrated to python 3.
# Or, more likely, migrate part of the project myself.
MIDDLEWARE_CLASSES += (#'htmlmin.middleware.HTMLMinMiddleware',
                       #'htmlmin.middleware.MarkRequestMiddleware',
                       )

STATIC_URL = 'https://s3.amazonaws.com/sparestub-staging/'
MEDIA_URL = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sparestub',
        'USER': 'postgres',
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),
        'HOST': '127.0.0.1'
    }
}

#ALLOWED_HOSTS = ['sparestub.com', 'www.sparestub.com']

AWS_BUCKET_NAME = 'sparestub-staging'
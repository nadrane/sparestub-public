__author__ = 'Nick'

from .base import *
from urllib.parse import urlparse
import dj_database_url

# Keep these in here always. regardless of what base.py says. Just be safe.
DEBUG = True
TEMPLATE_DEBUG = True

# Put on hold until https://github.com/cobrateam/django-htmlmin is migrated to python 3.
# Or, more likely, migrate part of the project myself.
MIDDLEWARE_CLASSES += (#'htmlmin.middleware.HTMLMinMiddleware',
                       #'htmlmin.middleware.MarkRequestMiddleware',
                       )

STATIC_URL = 'https://s3.amazonaws.com/sparestub-staging/static_root/'
MEDIA_URL = 'https://s3.amazonaws.com/sparestub-staging/media_root/'

#ALLOWED_HOSTS = ['sparestub.com', 'www.sparestub.com']

AWS_BUCKET_NAME = 'sparestub-staging'

es = urlparse(get_env_variable('SEARCHBOX_URL') or 'http://127.0.0.1:9200/')

port = es.port or 80

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': es.scheme + '://' + es.hostname + ':' + str(port),
        'INDEX_NAME': 'haystack',
    },
}

if es.username:
    HAYSTACK_CONNECTIONS['default']['KWARGS'] = {"http_auth": es.username + ':' + es.password}

# Make indexing happen whenever a model is saved or loaded
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
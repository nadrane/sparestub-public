from .base import *
from urllib.parse import urlparse

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

# Used to create links in emails to our site
DOMAIN = 'http://sparestub.com'

STRIPE_SECRET_API_KEY = get_env_variable('STRIPE_SECRET_API_KEY')
STRIPE_SECRET_API_KEY = get_env_variable('STRIPE_PUBLIC_API_KEY')

es = urlparse(os.environ.get('SEARCHBOX_URL') or 'http://127.0.0.1:9200/')

port = es.port or 80

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': es.scheme + '://' + es.hostname + ':' + str(port),
        'INDEX_NAME': 'haystack',
    },
}

#django-compressor settings
COMPRESS_OFFLINE_MANIFEST = 'production-manifest.json'

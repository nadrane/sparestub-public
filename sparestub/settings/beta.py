__author__ = 'Sparestub'

from .base import *
from urllib.parse import urlparse

# Keep these in here always. regardless of what base.py says. Just be safe.
DEBUG = True
TEMPLATE_DEBUG = True

STATIC_URL = 'https://s3.amazonaws.com/sparestub-production/static_root/'
MEDIA_URL = 'https://s3.amazonaws.com/sparestub-production/media_root/'

ALLOWED_HOSTS = ['beta.sparestub.com', 'sparestub-beta.herokuapp.com']

# Used to create links in emails to our site
DOMAIN = 'https://beta.sparestub.com'

STRIPE_SECRET_API_KEY = get_env_variable('STRIPE_SECRET_API_KEY')
STRIPE_PUBLIC_API_KEY = get_env_variable('STRIPE_PUBLIC_API_KEY')

es = urlparse(os.environ.get('SEARCHBOX_URL'))
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

# File Storage Backend Settings
DEFAULT_FILE_STORAGE = 'utils.backends.s3_boto.S3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'sparestub-production'

#django-compressor settings
COMPRESS_OFFLINE_MANIFEST = 'production-manifest.json'
COMPRESS_STORAGE = 'utils.backends.s3_boto.S3BotoStorage'
COMPRESS_ENABLED = True

# Celery Configuration
redis_url = urlparse(os.environ.get('REDISCLOUD_URL'))
BROKER_URL = redis_url
CELERY_RESULT_BACKEND = redis_url
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True}
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_SERIALIZER = 'json'
CELERYBEAT_MAX_LOOP_INTERVAL = 15


SEND_EMAILS = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

logging.basicConfig(level=logging.INFO)

# django-sslify Configuration
SSLIFY_DISABLE = False
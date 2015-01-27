__author__ = 'Nick'

from .base import *
from urllib.parse import urlparse

# Keep these in here always. regardless of what base.py says. Just be safe.
DEBUG = True
TEMPLATE_DEBUG = True

STATIC_URL = 'https://s3.amazonaws.com/sparestub-staging/static_root/'
MEDIA_URL = 'https://s3.amazonaws.com/sparestub-staging/media_root/'

ALLOWED_HOSTS = ['sparestub-staging.herokuapp.com', 'www.sparestub-staging.herokuapp.com']

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
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# File Storage Backend Settings
DEFAULT_FILE_STORAGE = 'utils.backends.s3_boto.S3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'sparestub-staging'

# Used to create links in emails to our site
DOMAIN = 'http://sparestub-staging.herokuapp.com'

STRIPE_SECRET_API_KEY = 'sk_test_gmA01wRhwK2cwkbGzdMHa00a'
STRIPE_PUBLIC_API_KEY = 'pk_test_6VZiRzF0eM4jjp3VJ7avVPZj'

#django-compressor settings
COMPRESS_OFFLINE_MANIFEST = 'staging-manifest.json'
COMPRESS_STORAGE = 'utils.backends.s3_boto.S3BotoStorage'
COMPRESS_ENABLED = True

SEND_EMAILS = True

# Celery Configuration
redis_url = urlparse(os.environ.get('REDISCLOUD_URL'))
BROKER_URL = redis_url
CELERY_RESULT_BACKEND = redis_url
BROKER_TRANSPORT_OPTIONS = {'fanout_prefix': True}
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_SERIALIZER = 'json'
CELERYBEAT_MAX_LOOP_INTERVAL = 15

logging.basicConfig(level=logging.INFO)
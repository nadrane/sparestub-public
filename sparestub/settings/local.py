from .base import *
from urllib.parse import urlparse

DEBUG = True
TEMPLATE_DEBUG = True

dirname = os.path.dirname

#INSTALLED_APPS += 'debug_toolbar',

STATICFILES_DIRS = (
    (os.path.join('sparestub', 'css'), os.path.join(BASE_DIR, 'static', 'css')),
    (os.path.join('sparestub', 'js'), os.path.join(BASE_DIR, 'static', 'js')),
    (os.path.join('sparestub', 'fonts'), os.path.join(BASE_DIR, 'static', 'fonts')),
    (os.path.join('sparestub', 'logos'), os.path.join(BASE_DIR, 'static', 'logos')),
    (os.path.join('sparestub', 'backgrounds'), os.path.join(BASE_DIR, 'static', 'backgrounds')),
)

# Serve from the local machine during development
STATIC_URL = '/static_root/'

# Serve from the local machine during development
MEDIA_URL = '/media_root/'

# This setting is for the syncs3.py management script.
# Safari does not know how to accept files ending in .gz, so we use .jgz instead.
SYNC_S3_RENAME_GZIP_EXT = '.jgz'
ZIPCODE_CSV = os.path.join(dirname(dirname(BASE_DIR)), 'locations', 'zipcode_database.csv')
ZIPCODE_JSON = os.path.join(dirname(dirname(BASE_DIR)), 'locations', 'zipcode_database.json')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sparestub',
        'USER': 'postgres',
        'PASSWORD': get_env_variable('DATABASE_PASSWORD'),
        'HOST': '127.0.0.1'
    }
}


es = urlparse(os.environ.get('SEARCHBOX_URL') or 'http://127.0.0.1:9200/')

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

# We really don't want sync_s3 changing the production or staging environents when run using
# the the dev environment. The only purpose for this bucket is testing the sync_s3 script.
# The sparestub-staging and sparestub-production buckets are used for staging and production, respectively
# File Storage Backend Settings
AWS_STORAGE_BUCKET_NAME = 'sparestub'

LOG_FILENAME = os.path.join(BASE_DIR, 'logging.txt')
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

# Make indexing happen whenever a model is saved or loaded
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Used to create links in emails to our site... and subdomain and method
DOMAIN = 'http://www.localhost:8000'

STRIPE_SECRET_API_KEY = 'sk_test_gmA01wRhwK2cwkbGzdMHa00a'
STRIPE_PUBLIC_API_KEY = 'pk_test_6VZiRzF0eM4jjp3VJ7avVPZj'

SEND_EMAILS = False
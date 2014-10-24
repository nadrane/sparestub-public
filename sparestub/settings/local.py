from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

dirname = os.path.dirname

STATICFILES_DIRS = (
    ('sparestub/css', os.path.join(BASE_DIR, 'static/css')),
    ('sparestub/js', os.path.join(BASE_DIR, 'static/js')),
    ('sparestub/fonts', os.path.join(BASE_DIR, 'static/fonts')),
    ('sparestub/logos', os.path.join(BASE_DIR, 'static/logos')),
)

# Serve from the local machine during development
STATIC_URL = '/static_root/'

# Serve from the local machine during development
MEDIA_URL = MEDIA_ROOT + '/'

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

# We really don't want sync_s3 changing the production or staging environents when run using
# the the dev environment. The only purpose for this bucket is testing the sync_s3 script.
# The sparestub-staging and sparestub-production buckets are used for staging and production, respectively
AWS_BUCKET_NAME = 'sparestub'

LOG_FILENAME = os.path.join(BASE_DIR, 'logging.txt')
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

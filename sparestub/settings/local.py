from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static/css'),
    os.path.join(BASE_DIR, 'static/js'),
    os.path.join(BASE_DIR, 'static/fonts'),
)

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static_root')

# Serve from the local machine during development
STATIC_URL = '/static_root/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media_root')

# Serve from the local machine during development
MEDIA_URL = MEDIA_ROOT + '/'

#TODO change me to postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# This setting is for the syncs3.py management script.
# Safari does not know how to accept files ending in .gz, so we use .jgz instead.
SYNC_S3_RENAME_GZIP_EXT = '.jgz'
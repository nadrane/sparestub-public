__author__ = 'nicholasdrane'

import os

# Needed if we fail to find an environment variable. Consult Pg. 39 of 2 scoops of Django
# Do not import other parts of the Django framework into the settings file
from django.core.exceptions import ImproperlyConfigured


def get_env_variable(var_name):
    """ Get the environment variable or return an exception """
    try:
        return os.environ.get(var_name, '')
    except KeyError:
        error_message = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_message)


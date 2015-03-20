__author__ = 'Spare Stub'

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


def reverse_category_lookup(input_key, category_list):
    for key, value in category_list:
        if input_key == key:
            return value


def reverse_dictionary(dictionary):
    return {value: key for key, value in dictionary.items()}


def get_variable_from_settings(variable, settings_module=''):
    if not settings_module:
        settings_module = get_env_variable('DJANGO_SETTINGS_MODULE')
    #http://docs.python.org/dev/library/functions.html#__import__
    return getattr(__import__(settings_module, fromlist=[variable]), variable)
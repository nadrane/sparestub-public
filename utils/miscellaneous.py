__author__ = 'nicholasdrane'

import os
import logging

import mandrill

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


def normalize_email(email):
    """
    Normalize the address by lowercasing the domain part of the email
    address.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = '@'.join([email_name, domain_part.lower()])
    return email


def send_email(to_email, subject, body, from_email, from_name='', **kwargs):
    """
    Generic function to send an email. We encapsulate the 3rd party API call in case we every change APIs

    returns: True - If the email sent successfully
             False - If the email failed to send
    """
    if not isinstance(to_email, list):
        to_email = [{'email': to_email}]

    if not from_name:
        from_name = from_email

    try:
        mandrill_client = mandrill.Mandrill(get_env_variable('MANDRILL_API_KEY'))

        # The contents of html will override the contents of body if both are present
        message = {'from_email': from_email,
                   'from_name': from_name,
                   'subject': subject,
                   'text': body,
                   'to': to_email,
                   'html': kwargs.get('html')
        }

        result = mandrill_client.messages.send(message=message, async=False)

        reject_reason = result[0].get('reject_reason')
        status = result[0].get('status')
        message_id = result[0].get('_id')

        if status in ['sent', 'queued', 'scheduled']:
            logging.info('email log: message id {} has been {}.'.format(message_id, status))
            return True
        elif status in ['rejected', 'invalid']:
            logging.warning('email log: message id {} has been {} because of {}'.
                            format(message_id, status, reject_reason))
            return False

    except mandrill.Error as e:
        # Mandrill errors are thrown as exceptions
        logging.critical('A mandrill error occurred: %s - %s' % (e.__class__, e))
        # TODO queue message and try again later and bolster logging


# Standard Imports
import logging

# 3rd Party Imports
from requests.exceptions import RequestException
from djrill import MandrillAPIError

# Django Imports
from django.core.mail import send_mail, EmailMultiAlternatives

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


def send_email(recipient_list, subject, message, from_email, from_name='', **kwargs):
    """
    Generic function to send an email. We encapsulate the 3rd party API call in case we every change APIs

    returns: True - If the email sent successfully
             False - If the email failed to send
    """

    if not isinstance(recipient_list, list):
        recipient_list = [recipient_list]

    if not from_name:
        from_name = from_email

    fail_silently = kwargs.get('fail_silently', False)

    try:
        if kwargs.get('html'):
            msg = EmailMultiAlternatives(subject=subject, from_email=from_email, to=recipient_list, body=message)
            msg.attach_alternative(kwargs.get('html'), 'text/html')
            msg.send(fail_silently=fail_silently)

        else:
            send_mail(subject, message, from_email, recipient_list, fail_silently=fail_silently)

    except MandrillAPIError as e:
         # Mandrill errors are thrown as exceptions
        logging.critical('A mandrill error occurred. Status code {}'.format(e.status_code))
        # TODO queue message and try again later and bolster logging

    except RequestException as e:
        # Generally occurs when the internet is not connected
        logging.critical('Cannot connect to email server: error {}'.format(str(e)))
        # TODO queue these up
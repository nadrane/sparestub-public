__author__ = 'nicholasdrane'

# Standard Imports
import json
import logging

# Django Imports
from django.http import HttpResponse


def ajax_http(contents, status=200, extra_json={}, **kwargs):
    '''
    Returns an HTTP response that we can use for asynchronous requests
    '''

    # contents should be a dictionary
    if callable(contents):
        contents = contents(**kwargs)

    if contents == True:
        contents = {'isSuccessful': True}

    if contents == False:
        contents = form_failure_notification('Uh Oh. Something went wrong over here.')

    contents.update(extra_json)

    return HttpResponse(json.dumps(contents),
                        content_type='application/json',
                        status=status
                        )

def non_field_errors_notification(form):
    """
        Return the first non_field_errors in json format ready to appear as a failure notification
    """
    try:
        message = form.non_field_errors()[0] # I can't think of a time when there is going to
                                             # be more than 1 error we need to return

        return form_failure_notification(message)
    except AttributeError:
        logging.error('non_field_errors_to_json called with no non_field_errors', stack_info=True, exc_info=True)
        return False # Returning false triggers a generic notification error message on the frontend


def form_success_notification(notification_content):
    """
        Trigger a green success notification bar to pop up on the client side with the enclosed message.
    """

    return {'contents': {'notification_type': 'alert-success',
                        'notification_content': notification_content},
            'status': 200}


def form_failure_notification(notification_content):
    """
        Trigger a red failure notification bar to pop up on the client side with the enclosed message.
    """

    return {'contents': {'notification_type': 'alert-danger',
                         'notification_content': notification_content},
            'status': 400}


def get_client_ip(request):
    '''
    Return the request user's ip address using the HTTP header.
    We will mostly use this function for logging to detect repeated attempts at intrusion from the same user.
    '''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
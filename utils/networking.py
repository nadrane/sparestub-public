__author__ = 'nicholasdrane'

import json

from django.http import HttpResponse
from django.shortcuts import render


def ajax_http(contents, status=200, **kwargs):
    '''
    Returns an HTTP response that we can use for asynchronous requests
    '''

    if callable(contents):
        contents = contents(**kwargs)

    if contents == True:
        contents = {'isSuccessful': True}

    if contents == False:
        contents = {'isSuccessful': False}



    return HttpResponse(json.dumps(contents),
                        content_type='application/json',
                        status=status
                        )


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
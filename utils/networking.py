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
# Core Python modules
import json
import logging

# Django core modules
from django.http import HttpResponse
from django.shortcuts import render

"""
# Crowd Surfer modules
from utils.cache import get_cache_contents
from utils.miscellaneous import PageType


def after_AJAX_login_HTTP_response(request, user):
    '''
    This is the HTTP response that will always be sent to the client after a user is authenticated and logged
    in asynchronously.
    At the moment, this is used in both the signup and login views
    '''

    json_response = {'navigation_bar_right_div': render(request,
                                                        'navigation_bar_right.html',
                                                        ).content.decode('utf-8')
                     }

    # At the moment, the contents of the works only differ based on over and under 18.
    # Thus, only age determines if we change the listings that are currently visible.
    # Obviously we don't show NSFW content by default
    # If we ever support custom front pages for logged in users, we will need to account for that here as well
    if user.over_18:
        json_response['listing_container'] = get_cache_contents(PageType.LISTING_PAGE, categories=None,
                                                                over_18=True, times_requested=0)

    return HttpResponse(json.dumps(json_response),
                        content_type='application/json'
                        )
"""

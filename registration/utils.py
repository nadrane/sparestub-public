# Django core modules
from django.shortcuts import render


def render_nav_bar(request, **kwargs):

    # This might happen since render_nav_bar is passed into ajax_http as a first class function
    contents = {'isSuccessful': True,
                'navigation_bar_right_div': render(request, 'navigation_bar_right.html').content.decode('utf-8')
                }

    return contents


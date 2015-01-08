# Django core modules
from django.shortcuts import render
from datetime import date

def render_nav_bar(request, **kwargs):

    # This might happen since render_nav_bar is passed into ajax_http as a first class function
    contents = {'isSuccessful': True,
                'navigation_bar_right_div': render(request, 'navigation_bar_right.html').content.decode('utf-8')
                }

    return contents


def calculate_age(birthdate):
    """
    Calculate a users age as of today.
    """

    if birthdate:
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return None

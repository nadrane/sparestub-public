# Django Imports
from django.conf import settings

# SpareStub Imports
from utils.miscellaneous import get_env_variable
from tickets.settings import ticket_submit_form_settings


def environment(request):
    environment_list = get_env_variable("DJANGO_SETTINGS_MODULE").split('.')
    environment_name = environment_list.pop(len(environment_list) - 1)
    return {'environment': environment_name}


def ticket_types(request):
    return {'TICKET_TYPES': ticket_submit_form_settings.get('TICKET_TYPES')}


def stripe_public_key(request):
    return {'stripe_public_api_key': settings.STRIPE_PUBLIC_API_KEY}
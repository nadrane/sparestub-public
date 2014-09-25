__author__ = 'nicholasdrane'

from utils.miscellaneous import get_env_variable


def environment(request):
    environment_list = get_env_variable("DJANGO_SETTINGS_MODULE").split('.')
    environment_name = environment_list.pop(len(environment_list) - 1)
    return {'environment': environment_name}
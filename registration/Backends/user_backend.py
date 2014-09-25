from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password

from registration.models import User


class PersonBackend(ModelBackend):
    '''
    https://github.com/django/django/blob/master/django/contrib/auth/backends.py
    Inherit from the original model so that we can just override the one authentication function.
    After all, that's all we want to change.
    '''
    def authenticate(self, email=None, password=None, fb_uid=None, fb_access_token=None):
        '''
        This authentication method tries to look up the user by both email address and by username
        '''
        if email and password:
            period_found = False
            at_found = False
            for char in email:
                if char == '@':
                    at_found = True
                elif char == '.':
                    period_found = True
            # If an email address was submitted, look up user via unique email
            if period_found and at_found:
                user = User.get_user_by_email(email)
                if user:
                    if user.check_password(password):
                        return user
        elif fb_uid and fb_access_token:
            user = User.get_user_by_fb_uid(fb_uid)
            if user and User.is_fb_access_token_valid(fb_uid, fb_access_token):
                return user
        else:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (Django ticket #20760).
            make_password(password)
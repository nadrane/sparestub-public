from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password

from registration.models import User


class UserBackend(ModelBackend):
    """
    https://github.com/django/django/blob/master/django/contrib/auth/backends.py
    Inherit from the original model so that we can just override the one authentication function.
    After all, that's all we want to change.
    """
    def authenticate(self, email=None, password=None, email_confirm_link=None):
        """
        This authentication method tries to look up the user by both email address and email confirmation link.
        We want to log users in after they click the email confirmation link, but the server won't have their password
        after they click it. Thus, we want to be able to authenticate a user solely based on that email link object.
        """
        user = None
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
                if not (user and user.check_password(password)):
                    user = None
        elif email_confirm_link:
            user = email_confirm_link.get_user_from_link()
        else:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (Django ticket #20760).
            make_password(password)
        return user
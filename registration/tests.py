"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

# Django modules
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

# Crowd Surfer modules
from .models import UserManager


class LoginViewTests(TestCase):
    @staticmethod
    def create_user():
        """
        Creates a person with an associated user record.
        """
        user = UserManager.create_user(email='ndrane@gmail.com', first_name='nick', last_name='drane', password='abcd')
        user.save()
        return user

    def test_get_without_authentication(self):
        """
        If the user is not authenticated, he should be directed a login screen
        """
        user = self.create_user()
        response = self.client.get(reverse('registration.views.signup'))
        self.assertEqual(response.status_code, 200)

    def test_get_with_authentication(self):
        """
        If the user is authenticated, he should be directed to the works
        """
        user = self.create_user()
        self.client.login(username='ndrane@gmail.com', password='abcd')
        response = self.client.get(reverse('registration.views.signup'))
        self.assertEqual(response.status_code, 200)


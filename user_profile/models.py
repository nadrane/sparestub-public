# Python core modules
import logging
from urllib.parse import urlparse
import re

# Django core modules
from django.db import models
from django.forms import ValidationError

# SpareStub imports
from .utils import calculate_age
from utils.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    #The username must be composed of numbers and upper and lower case letters
    username_regex = re.compile(r'^[a-zA-Z0-9]+$')

    # This is set in the User manager as opposed to here. This is because we need user email/name info. to create the username,
    # but the UserProfile needs to be created before the User because the User.user_profile cannot be null.
    username = models.CharField(max_length=254,  # This length comes from the max_length of an email address
                                db_index=True,
                                unique=True,
                                )

    # The number of times that this person's profile.html has been viewed by others.
    profile_views = models.IntegerField(default=0)

    birth_date = models.DateField(blank=True,
                                  null=True,
                                  default=None,
                                  )

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return '/profile/{}'.format(self.username)

    def age(self):
        return calculate_age(self.birth_date)

    @staticmethod
    def valid_username(username):
        if not re.match(UserProfile.username_regex, username):
            raise ValidationError("Your username can only contain letters and numbers.", code="bad username format")

    @staticmethod
    def contains_valid_scheme(parsed_url):
        if parsed_url.scheme != 'HTTP' and parsed_url.scheme != 'HTTPS' and parsed_url != '':
            return False

    @staticmethod
    def valid_website(website_url):
        '''
        Validate that a correctly formatted URL was submitted. Place some restrictions on protocol.
        Return a slightly cleaner version of the url submitted. Strip of query parameters and add a protocol.
        '''
        parsed_url = urlparse(website_url)
        if not UserProfile.contains_valid_scheme(parsed_url):
            raise ValidationError('The website URL must be HTTP or HTTPS.', code='invalid protocol')
        if parsed_url.scheme == '':
            parsed_url.scheme == "HTTP"
        return ''.join(parsed_url.scheme, '://', parsed_url.netloc)

    @staticmethod
    def user_profile_exists(username):
        username = username.lower()
        if UserProfile.objects.filter(username=username):
            return True
        return False

    @staticmethod
    def get_user_profile_from_url(username):
        username = username.lower()
        return UserProfile.objects.filter(username=username)[0]


    @staticmethod
    def make_profile_url(email, first_name, last_name):
        # Make sure that everything is lowercase
        email, first_name, last_name = email.lower(), first_name.lower(), last_name.lower()
        
        # Try to make the url equal to the users first and last names concatenated together
        potential_username = first_name + last_name
        if not UserProfile.user_profile_exists(potential_username):
            return potential_username

        # Try to make the url equal to the non-domain part of the user's email address
        # Emails are case sensitive, but our usernames will be all lowercase
        potential_username = email.split('@')[0].lower()
        if not UserProfile.user_profile_exists(potential_username):
            return potential_username

        # Make the user's url equal to his email with an appended number
        #TODO we really need to make sure this returns something
        number_to_append = 100
        while number_to_append < 100000:  # Let's make this finite just for safety
            potential_username = potential_username + str(number_to_append)
            if not UserProfile.user_profile_exists(potential_username):
                return potential_username
            number_to_append += 1


        logger = logging(__name__)
        logger.error("profile.html url did not generate properly for profile.html %s", email)
        return None


class ProfileQuestion(models.Model):
    question = models.CharField(blank=False,
                                max_length=254,
                                )


class ProfileAnswer(models.Model):
    user = models.ForeignKey(UserProfile,
                             blank=False,
                             )

    question = models.ForeignKey(ProfileQuestion)

    content = models.TextField(blank=True,
                               max_length=5000,
                               default=''
                               )
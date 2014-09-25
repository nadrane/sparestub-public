# Standard library modules
import re
import requests
import logging

# Django modules
from django.utils import timezone
from django.utils.http import urlquote
from django.db import models, transaction
from django.forms import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

# Crowd Surfer modules
from photos.models import Photo
from utils.models import TimeStampedModel, UserPostableModel
from .settings import user_model_settings
from utils.miscellaneous import get_variable_from_settings, normalize_email
from user_profile.models import UserProfile
from share.models import Listing


def random_user():
    return User.objects.order_by('?')[0]


def lookup_by_name(name, limit=5):
    '''
        Description: Return a list of users whose usernames start with the inputted string.
                     The case of the inputted text is ignored, since usernames are case-insensitive.
        Parameters:
            limit - The number of users to return
            name  - The substring to whose characters are the beginning of the usernames we want to return.

        returns: A list of DisplayObjects, which represent information about users.
                 The objects will contain a username and a profile.html picture.
    '''
    userList = []

    class UserObject:
        def __init__(self, username, photoURL):
            self.username = username
            self.photoURL = photoURL

    users = User.objects.filter(username__istartswith=name)[:limit].only('user_profile__profile_picture', 'username')

    if users:
        for user in users:
            userList.append(UserObject(user.username, user.profile_picture))

    return userList


class UserManager(BaseUserManager):

    @transaction.atomic()  # We definitely do not want to create a User record without a UserProfile
    def _create_user(self, email, password, first_name, last_name, is_staff, is_superuser, facebook_user_id=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """

        # Remember that the database requires an integer, not a string, which is likely what we got as an argument.
        if facebook_user_id:
            facebook_user_id = int(facebook_user_id)
        # If an empty string is passed in, we hit this case. An empty string will actually cause a server error in the
        # model if we try to save it to the database.
        else:
            facebook_user_id = None

        if not email and not facebook_user_id:
            raise ValueError('User has neither a facebook user id nor an email address.')

        user_profile = UserProfile()
        user_profile.username = UserProfile.make_profile_url(email, first_name, last_name)
        user_profile.save()

        email = self.normalize_email(email)
        user = self.model(email=email,
                          first_name=first_name,
                          last_name=last_name,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          user_profile=user_profile,
                          facebook_user_id=facebook_user_id,
                          **extra_fields
                          )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, first_name, last_name, facebook_user_id=None, **extra_fields):
        return self._create_user(email,
                                 password,
                                 first_name,
                                 last_name,
                                 False,
                                 False,
                                 facebook_user_id,
                                 **extra_fields
                                 )

    def create_superuser(self, email, password, first_name, last_name, facebook_user_id=None, **extra_fields):
        return self._create_user(email,
                                 password,
                                 first_name,
                                 last_name,
                                 True,
                                 True,
                                 facebook_user_id,
                                 **extra_fields
                                 )


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel, UserPostableModel):
    """
    A fully featured User model with admin-compliant permissions that uses a full-length email field as the username.

    Email and password are required. Other fields are optional.
    """


    email = models.EmailField('email address',
                              max_length=user_model_settings['EMAIL_MAX_LENGTH'],
                              unique=True,
                              blank=False
                              )

    user_profile = models.OneToOneField(UserProfile,
                                        null=False,
                                        )

    first_name = models.CharField('first name',
                                  max_length=user_model_settings['FIRST_NAME_MAX_LENGTH'],
                                  blank=False
                                  )

    last_name = models.CharField('last name',
                                 max_length=user_model_settings['LAST_NAME_MAX_LENGTH'],
                                 blank=False
                                 )

    profile_picture = models.OneToOneField(Photo,
                                           null=True,
                                           blank=True,
                                           default=None,
                                           )

    is_staff = models.BooleanField('staff status',
                                   default=False,
                                   help_text=('Designates whether the user can log into this admin site.')
                                   )

    # Every Facebook account has an associated User ID. This ID is passed to our server via the FB API when the user logs in.
    # Store this ID, primarily because we only want there to be one Crowdsurfer account per FB account.
    facebook_user_id = models.IntegerField('facebook user ID',
                                           null=True,
                                           blank=True,
                                           default=None
                                           )

    # Why was this account marked as inactive. Cannot be part of UserPostableModel becomes choices will be different
    # for every model that inherits the UserPostableModelMixin.
    deactivation_reason = models.CharField(max_length=200,
                                           choices=user_model_settings['DEACTIVATION_REASON'],
                                           help_text='Explains why the user account is now inactive.',
                                           null=True,
                                           blank=True,
                                           default=None,
                                           )


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = ('user')
        verbose_name_plural = ('users')

    @staticmethod
    def user_exists(email):
        '''
        Since the email is unique for every user, we can check for the existence of a user by querying by email
        '''
        # Note that the non-domain part of an email address is case sensitive, so we need email__exact
        if User.objects.filter(email__iexact=email):
            return True
        return False

    def get_absolute_url(self):
        return "/profile.html/%s/" % urlquote(self.user_profile.username)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name.capitalize(), self.last_name.capitalize())
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, get_variable_from_settings('DEFAULT_FROM_EMAIL'), [self.email])

    def active_submissions(self):
        '''
        Returns the number of listings that this user has submitted that are still active.
        '''
        return Listing.objects.filter(poster=self).filter(active=True).count()

    @staticmethod
    def name_contains_explicit_language(name):
        if isinstance(name, str):
            name = re.split(' ', name)  # Remember that a name might contain spaces.

        # There are actually quite a few first and last names that are composed of multiple words separated by spaces.
        for word in name:
            if word in user_model_settings['EXPLICIT_WORD_LIST']:
                return True
        return False

    @staticmethod
    def name_contains_invalid_characters(name):
        # Verify that the name contains only letters and spaces. We can internationalize this at some point.
        if not re.match("[A-Za-z ]*$", name):
            return True
        return False

    @staticmethod
    def valid_name(name):
        '''
        Description: To be used during form validation!!!
                     Takes a input name string and
                        __init__() got an unexpected keyword argument. Removes multiple consecutive spaces.
                        2. Validates that the name does not contain numbers or symbols.
                        3. Flags it for containing explicit language
        Parameter:
            name - an input string
        Returns: The input name parameter with consecutive spaces removed and all words capitalized
        '''

        word_list = re.split(' ', name)  # Remove consecutive spaces from the name

        if User.name_contains_explicit_language(word_list):
            raise ValidationError('Names cannot contain explicit language', code='explicit language')

        new_name = " ".join([word for word in word_list])

        # Verify that the nae contains only letters and spaces. We can internationalize this at some point.
        if User.name_contains_invalid_characters(new_name):
            raise ValidationError('Names may only contain letters and spaces', code='bad format')

        return new_name

    def equal_to_current_password(self, password_input):
        '''
        Check to see if an inputted password matches the user's password
        '''
        return self.password == password_input

    @staticmethod
    def valid_email(email):
        '''
        Make sure that this email address does not already exist in the database
        '''
        email = normalize_email(email)
        # Even though the database only contains lowercase emails, consider case-sensitivity. Just as an extra error check
        if User.user_exists(email):
            raise ValidationError('Email already exists. Please select a new email.', code="email_exists")
        #Store the normalized email in the database
        return email

    @staticmethod
    def facebook_user_id_exists(fb_uid):
        '''
        Allow each facebook account to be linked to a single Crowdsurfer account. Enforce this here.
        This means that if we ban a user account, we are also banning his entire social network.
        This makes cheating the system extremely risky.
        '''
        if User.objects.filter(facebook_user_id=fb_uid):
            return True
        return False

    @staticmethod
    def valid_facebook_user_id(fb_uid):
        if User.facebook_user_id_exists(fb_uid):
            raise ValidationError('Facebook account already registered to another account. \
            Please user a different account.', code="fb_uid_exists")
        return fb_uid

    @staticmethod
    def get_user_by_fb_uid(fb_uid):
        '''
        A helper function to look up users based on their unique facebook user ID
        '''
        user = User.objects.filter(facebook_user_id__exact=fb_uid)
        if user:
            return user[0]
        return None

    @staticmethod
    def is_fb_access_token_valid(fb_uid, fb_access_token):
        if not fb_uid or not fb_access_token:
            return False
        response = requests.get('https://graph.facebook.com/me', params={'access_token': fb_access_token})
        response_json = response.json()
        # This is incredibly important!! We need to make sure that the facebook user ID that the user sent us is the
        # same one that they authenticated with. Otherwise, the user could authenticate with FB as one user but send
        # us any old users user id.
        response_json['id'] = str(response_json['id'])  # Currently a string, but be safe
        fb_uid = str(fb_uid)  # This likely is an integer
        if response_json['id'] != fb_uid:
            logging.critical('fb_uid has been tampered with.')
            return False
        return True


    @staticmethod
    def get_user_by_email(email):
        '''
        A helper function to look up users based on their unique email address
        '''
        user = User.objects.filter(email__exact=email)
        if user:
            return user[0]
        return None

    def __str__(self):
        return self.get_full_name()

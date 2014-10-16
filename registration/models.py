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

from utils.models import TimeStampedModel
#from user_profile.models import UserProfile
from .settings import user_model_settings
from utils.miscellaneous import get_variable_from_settings


# Crowd Surfer modules
from photos.models import Photo
from utils.models import TimeStampedModel
from .settings import user_model_settings
from utils.miscellaneous import get_variable_from_settings
from utils.email import send_mail, normalize_email
from user_profile.models import UserProfile


class UserManager(BaseUserManager):

    @transaction.atomic()  # We definitely do not want to create a User record without a UserProfile
    def _create_user(self, email, password, first_name, last_name, is_staff, is_superuser, **extra_fields):

        '''Creates and saves a User with the given email and password.'''

        if not email:
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
                          **extra_fields
                          )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, first_name, last_name, **extra_fields):
        return self._create_user(email,
                                 password,
                                 first_name,
                                 last_name,
                                 False,
                                 False,
                                 **extra_fields
                                 )

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        return self._create_user(email,
                                 password,
                                 first_name,
                                 last_name,
                                 True,
                                 True,
                                 **extra_fields
                                 )


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
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

    zipcode = models.IntegerField(max_length=5,
                                  null=False,
                                  blank=False,
                                  )

    is_staff = models.BooleanField('staff status',
                                   default=False,
                                   help_text=('Designates whether the user can log into this admin site.')
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
        """
        Since the email is unique for every user, we can check for the existence of a user by querying by email
        """
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
        """
        Returns the short name for the user."
        """

        return self.first_name

    #TODO email function needs to use sendgrid or mandrill.
    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """

        send_mail(subject, message, get_variable_from_settings('DEFAULT_FROM_EMAIL'), [self.email])

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
        Parameter:
            name - an input string
        Returns: The input name parameter with consecutive spaces removed and all words capitalized
        '''

        word_list = re.split(' ', name)  # Remove consecutive spaces from the name
        new_name = " ".join([word for word in word_list])

        # Verify that the nae contains only letters and spaces. We can internationalize this at some point.
        if User.name_contains_invalid_characters(new_name):
            raise ValidationError('Names may only contain letters and spaces', code='bad_format')

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
            raise ValidationError('That email address is already registered', code="email_exists")
        #Store the normalized email in the database
        return email

    @staticmethod
    def valid_zipcode(zipcode):
        if not re.match('^\d{5}$', zipcode):
            raise ValidationError('That zipcode is not valid', code="invalid_zipcode_format")
        return zipcode

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

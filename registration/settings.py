from datetime import timedelta
from django.utils import timezone

over_18_year_date = None #timezone.now() - timedelta(years=18)

user_model_settings = {'PASSWORD_MIN_LENGTH': 6,
                       'PASSWORD_MAX_LENGTH': 128,  # Don't edit this. This value is defined in
                                                    # django / contrib / auth / models.py / AbstractBaseUser

                       'FIRST_NAME_MAX_LENGTH': 20,
                       'LAST_NAME_MAX_LENGTH': 20,
                       'EMAIL_MAX_LENGTH': 254,

                       'DEACTIVATION_REASON': (),

                       'GENDER_CHOICES': (
                                          ('M', 'Freshman'),
                                          ('F', 'Sophomore'),
                                          ),

                       'ZIP_CODE_MAX_LENGTH': 5,
                       }

password_form_settings = {'PASSWORD_NOTEMPTY_MESSAGE': 'Please enter a password.',
                          'PASSWORD_MIN_LENGTH': user_model_settings['PASSWORD_MIN_LENGTH'],
                          'PASSWORD_MAX_LENGTH': user_model_settings['PASSWORD_MAX_LENGTH'],
                          'PASSWORD_LENGTH_MESSAGE': 'Please keep your password between %s and %s characters' %
                                                  (user_model_settings['PASSWORD_MIN_LENGTH'],
                                                   user_model_settings['PASSWORD_MAX_LENGTH'],
                                                   ),

                          'PASSWORD_REMOTE_MESSAGE': "That's not your password!",
                          'PASSWORD_IDENTICAL_MESSAGE': 'Your passwords do not match!'
                          }


email_form_settings = {'EMAIL_MAX_LENGTH': user_model_settings['EMAIL_MAX_LENGTH'],
                       'EMAIL_NOTEMPTY_MESSAGE': 'Please enter an email address.',
                       'EMAIL_EMAILADDRESS_MESSAGE': 'The inputted email address is not valid.',
                       'EMAIL_LENGTH_MESSAGE': 'Please keep your email address fewer than %s characters.' %
                       user_model_settings['EMAIL_MAX_LENGTH'],
                       'EMAIL_REMOTE_MESSAGE': 'That email is already registered to another account.'
                       }

user_info_form_settings = {'FIRST_NAME_NOTEMPTY_MESSAGE': 'Please enter your first name.' ,
                           'FIRST_NAME_MAX_LENGTH': user_model_settings['FIRST_NAME_MAX_LENGTH'],
                           'FIRST_NAME_LENGTH_MESSAGE': 'Please keep your first name fewer than %s characters' %
                           user_model_settings['FIRST_NAME_MAX_LENGTH'],
                           'FIRST_NAME_REGEXP': '^[a-zA-Z ]+$', # Note that this is javascript. If this changes,
                                                                # the serverside validator MUST change as well.
                           'FIRST_NAME_REGEXP_MESSAGE': 'Your first name can only contain alphabetical characters and spaces',


                           'LAST_NAME_NOTEMPTY_MESSAGE': 'Please enter your last name',
                           'LAST_NAME_MAX_LENGTH': user_model_settings['LAST_NAME_MAX_LENGTH'],
                           'LAST_NAME_LENGTH_MESSAGE': 'Please keep your last name fewer than %s characters' %
                           user_model_settings['LAST_NAME_MAX_LENGTH'],
                           'LAST_NAME_REGEXP': '^[a-zA-Z ]+$',  # Note that this is javascript. If this changes,
                                                                # the serverside validator MUST change as well.
                           'LAST_NAME_REGEXP_MESSAGE': 'Your last name can only contain alphabetical characters and spaces',

                           'BIRTHDATE_NOTEMPTY_MESSAGE': 'Please enter your birthdate',
                           'BIRTHDATE_DATE_FORMAT': 'MM/DD/YYYY',
                           'BIRTHDATE_DATE_MESSAGE': 'Please enter your birthdate in MM/DD/YYYY format.',
                           'BIRTHDATE_DATE_SEPARATOR': '/',

                           'ZIP_CODE_NOTEMPTY_MESSAGE': 'Please enter your zipcode',
                           'ZIP_CODE_MAX_LENGTH': user_model_settings.get('ZIP_CODE_MAX_LENGTH'),
                           'ZIP_CODE_MIN_LENGTH': user_model_settings.get('ZIP_CODE_MAX_LENGTH'),
                           'ZIP_CODE_LENGTH_MESSAGE': 'We only need a {} digit zipcode'.format(user_model_settings.get('ZIP_CODE_MAX_LENGTH'),),
                           'ZIP_CODE_REMOTE_MESSAGE': 'That is not a valid zip code',

                           # Note that this regx is actually wrong. It matches 1 through 5 digits.
                           # We want to avoid having this error fire when less than 5 digits have been entered since the
                           # error message would be otherwise misleading.
                           # The length validator kicks into play when the length is wrong.
                           'ZIP_CODE_REGEXP': '^\d{1,5}$',  # Note that this is javascript. If this changes,
                                                           # the serverside validator MUST change as well.

                           'ZIP_CODE_REGEXP_MESSAGE': 'Your zipcode should only contain numbers',
                           }

user_info_form_settings.update(email_form_settings)

signup_form_settings = {}
signup_form_settings.update(user_info_form_settings)
signup_form_settings.update(password_form_settings)

login_form_settings = {}
login_form_settings.update(email_form_settings)
login_form_settings.update(password_form_settings)

PASSWORD_RESET_EMAIL_SUBJECT = 'SpareStub - Reset your password'
PASSWORD_RESET_EMAIL_TEMPLATE = 'registration/forgot_password_email.html'
EMAIL_CONFIRMATION_EMAIL_SUBJECT = 'SpareStub - Email confirmation'
EMAIL_CONFIRMATION_EMAIL_TEMPLATE = 'registration/email_confirmation_email.html'

DEFAULT_PROFILE_PIC_URL = 'sparestub/logos/lilman.jpg'
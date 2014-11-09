# Django Imports
from django.core.urlresolvers import reverse

# SpareStub Imports
from registration.settings import user_info_form_settings
from registration.models import user_model_settings

profile_question_model_settings = {'QUESTION_MAX_LENGTH': 254}

profile_answer_model_settings = {'CONTENT_MAX_LENGTH': 5000}

user_profile_model_settings = {'USERNAME_MAX_LENGTH': user_model_settings.get("FIRST_NAME_MAX_LENGTH") +
                                                      user_model_settings.get('LAST_NAME_MAX_LENGTH') + 40
                                                      # The username must be at least as long as the sum of the first
                                                      # and last names + 6 (the auto-appended numbers in make_username).
                                                      # THe additional 34 characters are pretty arbitrary.
                               }

edit_profile_form_settings = {'USERNAME_NOTEMPTY_MESSAGE': 'Please enter your username.' ,
                              'USERNAME_MAX_LENGTH': user_profile_model_settings.get('USERNAME_MAX_LENGTH'),
                              'USERNAME_LENGTH_MESSAGE': 'Please keep your first name fewer than {} characters'
                              .format(user_profile_model_settings.get('USERNAME_MAX_LENGTH')),
                              'USERNAME_REGEXP': '^[a-zA-Z1-9]+$', # Note that this is javascript. If this changes,
                                                                # the serverside validator MUST change as well.
                              'USERNAME_REGEXP_MESSAGE': 'Your first name can only contain alphabetical characters and spaces',

                              # The actual remote URL is added in views.py for circular dependency reasons
                              'USERNAME_REMOTE_MESSAGE': 'That username already exists. Please pick another.'
                              }

edit_profile_form_settings.update(user_info_form_settings)
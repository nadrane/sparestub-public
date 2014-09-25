__author__ = 'Nick'

user_model_settings = {'PASSWORD_MIN_LENGTH': 6,
                       'PASSWORD_MAX_LENGTH': 128,  # Don't edit this. This value is defined in
                                                    # django / contrib / auth / models.py / AbstractBaseUser

                       'FIRST_NAME_MAX_LENGTH': 30,
                       'LAST_NAME_MAX_LENGTH': 30,
                       'EMAIL_MAX_LENGTH': 254,

                       'DEACTIVATION_REASON': (),
                       'EXPLICIT_WORD_LIST': []
                       }

signup_form_settings = {'PASSWORD_NOTEMPTY_MESSAGE': 'Please enter a password.',
                        'PASSWORD_MIN_LENGTH': user_model_settings['PASSWORD_MIN_LENGTH'],
                        'PASSWORD_MAX_LENGTH': user_model_settings['PASSWORD_MAX_LENGTH'],
                        'PASSWORD_LENGTH_MESSAGE': 'Please keep your password between %s and %s characters.' %
                                                   (user_model_settings['PASSWORD_MIN_LENGTH'],
                                                    user_model_settings['PASSWORD_MAX_LENGTH'],
                                                    ),

                        'FIRST_NAME_NOTEMPTY_MESSAGE': 'Please enter your first name.' ,
                        'FIRST_NAME_MAX_LENGTH': user_model_settings['FIRST_NAME_MAX_LENGTH'],
                        'FIRST_NAME_LENGTH_MESSAGE': 'Please keep your first name fewer than %s characters' %
                        user_model_settings['FIRST_NAME_MAX_LENGTH'],
                        'FIRST_NAME_REGEXP': '^[a-z\s]+$', # Note that this is javascript. If this changes,
                                                             # the serverside validator MUST change as well.
                        'FIRST_NAME_REGEXP_MESSAGE': 'Your first name can only contain alphabetical characters and spaces',


                        'LAST_NAME_NOTEMPTY_MESSAGE': 'Please enter your last name.',
                        'LAST_NAME_MAX_LENGTH': user_model_settings['LAST_NAME_MAX_LENGTH'],
                        'LAST_NAME_LENGTH_MESSAGE': 'Please keep your last name fewer than %s characters' %
                        user_model_settings['LAST_NAME_MAX_LENGTH'],
                        'LAST_NAME_REGEXP': '^[a-z\s]+$',  # Note that this is javascript. If this changes,
                                                             # the serverside validator MUST change as well.
                        'LAST_NAME_REGEXP_MESSAGE': 'Your last name can only contain alphabetical characters and spaces',


                        'EMAIL_MAX_LENGTH': user_model_settings['EMAIL_MAX_LENGTH'],
                        'EMAIL_NOTEMPTY_MESSAGE': 'Please enter an email address.',
                        'EMAIL_EMAILADDRESS_MESSAGE': 'The inputted email address is not valid.',
                        'EMAIL_LENGTH_MESSAGE': 'Please keep your email address fewer than %s characters.' %
                        user_model_settings['EMAIL_MAX_LENGTH']
                        }

login_form_settings = {'PASSWORD_NOTEMPTY_MESSAGE': 'Please enter a password.',

                       'EMAIL_MAX_LENGTH': user_model_settings['EMAIL_MAX_LENGTH'],
                       'EMAIL_NOTEMPTY_MESSAGE': 'Please enter an email address.',
                       'EMAIL_EMAILADDRESS_MESSAGE': 'The inputted email address is not valid.',
                       'EMAIL_LENGTH_MESSAGE': 'Please keep your email address fewer than %s characters.' %
                       user_model_settings['EMAIL_MAX_LENGTH']
                       }

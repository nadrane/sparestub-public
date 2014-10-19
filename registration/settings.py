__author__ = 'Nick'

user_model_settings = {'PASSWORD_MIN_LENGTH': 6,
                       'PASSWORD_MAX_LENGTH': 128,  # Don't edit this. This value is defined in
                                                    # django / contrib / auth / models.py / AbstractBaseUser

                       'FIRST_NAME_MAX_LENGTH': 30,
                       'LAST_NAME_MAX_LENGTH': 30,
                       'EMAIL_MAX_LENGTH': 254,

                       'DEACTIVATION_REASON': (),

                       'GENDER_CHOICES': (
                                          ('M', 'Freshman'),
                                          ('F', 'Sophomore'),
                                          )
                       }

signup_form_settings = {'PASSWORD_NOTEMPTY_MESSAGE': 'Please enter a password.',
                        'PASSWORD_MIN_LENGTH': user_model_settings['PASSWORD_MIN_LENGTH'],
                        'PASSWORD_MAX_LENGTH': user_model_settings['PASSWORD_MAX_LENGTH'],
                        'PASSWORD_LENGTH_MESSAGE': 'Please keep your password between %s and %s characters' %
                                                   (user_model_settings['PASSWORD_MIN_LENGTH'],
                                                    user_model_settings['PASSWORD_MAX_LENGTH'],
                                                    ),

                        'FIRST_NAME_NOTEMPTY_MESSAGE': 'Please enter your first name.' ,
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


                        'EMAIL_MAX_LENGTH': user_model_settings['EMAIL_MAX_LENGTH'],
                        'EMAIL_NOTEMPTY_MESSAGE': 'Please enter an email address',
                        'EMAIL_EMAILADDRESS_MESSAGE': 'The inputted email address is not valid',
                        'EMAIL_LENGTH_MESSAGE': 'Please keep your email address fewer than %s characters' %
                        user_model_settings['EMAIL_MAX_LENGTH'],

                        'ZIPCODE_NOTEMPTY_MESSAGE': 'Please enter your zipcode',
                        'ZIPCODE_MAX_LENGTH': 5,
                        'ZIPCODE_MIN_LENGTH': 5,
                        'ZIPCODE_LENGTH_MESSAGE': 'We only need a 5 digit zipcode',

                        # Note that this regx is actually wrong. It matches 1 through 5 digits.
                        # We want to avoid having this error fire when less than 5 digits have been entered since the
                        # error message would be otherwise misleading.
                        # The length validator kicks into play when the length is wrong.
                        'ZIPCODE_REGEXP': '^\d{1,5}$',  # Note that this is javascript. If this changes,
                                                        # the serverside validator MUST change as well.

                        'ZIPCODE_REGEXP_MESSAGE': 'Your zipcode should only contain numbers',
                        }

login_form_settings = {'PASSWORD_NOTEMPTY_MESSAGE': 'Please enter a password.',
                       'PASSWORD_MIN_LENGTH': user_model_settings['PASSWORD_MIN_LENGTH'],
                       'PASSWORD_MAX_LENGTH': user_model_settings['PASSWORD_MAX_LENGTH'],
                       'PASSWORD_LENGTH_MESSAGE': 'Please keep your password between %s and %s characters' %
                                                  (user_model_settings['PASSWORD_MIN_LENGTH'],
                                                   user_model_settings['PASSWORD_MAX_LENGTH'],
                                                   ),

                       'EMAIL_MAX_LENGTH': user_model_settings['EMAIL_MAX_LENGTH'],
                       'EMAIL_NOTEMPTY_MESSAGE': 'Please enter an email address.',
                       'EMAIL_EMAILADDRESS_MESSAGE': 'The inputted email address is not valid.',
                       'EMAIL_LENGTH_MESSAGE': 'Please keep your email address fewer than %s characters.' %
                       user_model_settings['EMAIL_MAX_LENGTH']
                       }

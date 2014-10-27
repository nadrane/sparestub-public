contact_form_settings = {'SUBJECT_TYPES':
                         [('Q', 'Question'),
                          ('R', 'Report Bug'),
                          ('S', 'Suggestion'),
                          ('U', 'Sign Up for Updates')
                          ],
                         'BODY_MINLENGTH': 0,
                         'BODY_MAXLENGTH': 5000,
                         'EMAIL_NOTEMPTY_MESSAGE': "Please enter an email address.",
                         'EMAIL_EMAILADDRESS_MESSAGE': "This email address is not valid.",
                         'SUBJECT_TYPE_NOTEMPTY_MESSAGE': "Please select a subject for your message.",
                         'BODY_NOTEMPTY_MESSAGE': "Don't forget to write something!",
                         'EMAIL_MAXLENGTH': 254,
                         }

# These keys need to be defined after their respective MINLENGTH and MAXLENGTH keys
#  have been defined to avoid key errors.
contact_form_settings['BODY_LENGTH_MESSAGE'] = "Please keep your message between %s and %s characters." % \
                                               (contact_form_settings['BODY_MINLENGTH'],
                                                contact_form_settings['BODY_MAXLENGTH']
                                                )

contact_form_settings['EMAIL_LENGTH_MESSAGE'] = 'Please keep your email address fewer than %s characters.' % \
                                                 contact_form_settings['EMAIL_MAXLENGTH']

auto_response_subject = 'Thanks From SpareStub!'
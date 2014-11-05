from datetime import date
from locations.settings import states

ticket_model_settings = {'TITLE_MAX_LENGTH': 300,
                         'CONTENT_MAX_LENGTH': 10000,
                         'TICKET_TYPES': (('M', 'Music'),
                                          ('S', 'Sports'),
                                          ('T', 'Theatre'),
                                          ('C', 'Comedy'),
                                          ('O', 'Other'),
                                          ),
                         'PAYMENT_METHODS': (('G', 'Good Faith'),
                                             ('S', 'Secure'),
                                             ),

                         'DEACTIVATION_REASONS': (('C', 'Cancelled'),  # User cancelled ticket
                                                  ('E', 'Expired'),  # Event date has passed
                                                  ('S', 'Sold'), # Ticket sold to another user
                                                  ('D', 'Deactivated') # User account deactivated with active tickets
                                                  )
                         }

ticket_submit_form_settings = {'TITLE_NOTEMPTY_MESSAGE': 'Please enter a title',
                               'TITLE_MAX_LENGTH': ticket_model_settings.get('TITLE_MAX_LENGTH'),
                               'TITLE_LENGTH_MESSAGE': "You're title cannot exceed {} characters"
                                   .format(ticket_model_settings.get('TITLE_MAX_LENGTH')),

                               'CONTENT_MAX_LENGTH': ticket_model_settings.get('CONTENT_MAX_LENGTH'),
                               'CONTENT_LENGTH_MESSAGE': "You're post cannot exceed {} characters"
                                    .format(ticket_model_settings.get('CONTENT_MAX_LENGTH')),

                               'TICKET_TYPES': ticket_model_settings.get('TICKET_TYPES'),
                               'TICKET_TYPE_NOTEMPTY_MESSAGE': 'Please select the type of event',

                               'PRICE_NOTEMPTY_MESSAGE': 'Please enter a ticket price',
                               'PRICE_NUMERIC_SEPARATOR': '.',
                               'PRICE_NUMERIC_MESSAGE': 'Please enter a number',
                               'PRICE_MIN_VALUE': '0.00',
                               'PRICE_MAX_VALUE': '1000000.00',

                               'START_DATE_NOTEMPTY_MESSAGE': 'Please enter the date event starts',
                               'START_DATE_DATE_FORMAT': 'MM/DD/YYYY',
                               'START_DATE_DATE_MESSAGE': 'Please click the calendar icon to select a date in correct format (MM/DD/YYYY)',
                               'START_DATE_DATE_SEPARATOR': '/',

                               'START_TIME_NOTEMPTY_MESSAGE': 'Please enter the time event starts',
                               'START_TIME_REGEXP': '^(0?[1-9]|1[012])(:[0-5]\d) ?[APap][mM]$',
                                # Note that this is javascript. If this changes, the serverside validator MUST change as well.
                               'START_TIME_REGEXP_MESSAGE': 'Please click the clock to select a time in the correct format (HH:MM AM/PM)',

                               'LOCATION_NOTEMPTY_MESSAGE': 'Please enter the city and state where the event takes place',

                               'PAYMENT_METHODS': ticket_model_settings.get('PAYMENT_METHODS'),
                               'PAYMENT_METHOD_NOTEMPTY_MESSAGE': 'Please select a payment method',
                            }

search_results_settings = {'TICKET_TYPES': ticket_model_settings.get('TICKET_TYPES'),
                           'PAYMENT_METHODS': ticket_model_settings.get('PAYMENT_METHODS')
                           }

email_submit_ticket_subject = 'SpareStub has received your ticket submission!'
from datetime import date

ticket_model_settings = {'TITLE_MAX_LENGTH': 300,
                         'CONTENT_MAX_LENGTH': 10000,
                         'TICKET_TYPES': (('M', 'Music'),
                                          ('S', 'Sports'),
                                          ('T', 'Theatre'),
                                          ('C', 'Comedy'),
                                          ('O', 'Other')
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

                               'START_DATETIME_NOTEMPTY_MESSAGE': 'Please enter the date and time the event starts',
                               'START_DATETIME_DATE_FORMAT': 'MM/DD/YYYY h:m A',
                               'START_DATETIME_DATE_MESSAGE': 'Please use the date picker to select a date in correct format.',
                               'START_DATETIME_DATE_SEPARATOR': '/',
                               'TODAYS_DATE': date.today(),

                               'LOCATION_NOTEMPTY_MESSAGE': 'Please enter the city and state where the event takes place',
                         }
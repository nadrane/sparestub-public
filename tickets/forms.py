# Standard Imports
import logging
import datetime

# Django Imports
from django import forms
from django.utils import timezone

# SpareStub Imports
from .settings import ticket_submit_form_settings
from locations.models import Location, Alias, map_citystate_to_location, LocationMatchingException
from utils.fields import CurrencyField


class SubmitTicketForm(forms.Form):
    price = CurrencyField(required=True,
                          min_value=float(ticket_submit_form_settings.get('PRICE_MIN_VALUE')),
                          max_value=float(ticket_submit_form_settings.get('PRICE_MAX_VALUE')),
                          localize=True, # We want to sanitize the input for comma and decimal separators.
                          )

    title = forms.CharField(required=True,
                            max_length=ticket_submit_form_settings.get('TITLE_MAX_LENGTH'),
                            )

    location_raw = forms.CharField(required=True,
                                   max_length=200
                                   )

    zip_code = forms.CharField(required=True)  # Not explicitly entered by the user but determined using the
                                               # city and state in location_raw

    start_date = forms.DateField(required=True)

    start_time = forms.TimeField(required=True,
                                 input_formats=['%H:%M %p'])  # Format of hours:minutes AM/PM

    type = forms.ChoiceField(required=True,
                             choices=ticket_submit_form_settings.get('TICKET_TYPES'))

    payment_method = forms.ChoiceField(required=True,
                                       choices=ticket_submit_form_settings.get('PAYMENT_METHODS'))

    def handle_location(self):
        zip_code_location = Location.objects.filter(zip_code=self.cleaned_data.get('zip_code'))

        if not zip_code_location:
            raise forms.ValidationError('Invalid zip code returned.', code='invalid_zip_code')
        else:
            zip_code_location = zip_code_location[0]

        city, state = map(lambda x: x.strip().lower(), self.cleaned_data.get('location_raw').split(','))

        try:
            city_state_location = map_citystate_to_location(city, state)
        except LocationMatchingException as e:
            logging.error(e.msg + 'location_raw: {} and zip_code: {}'.format(self.cleaned_data.get('location'),
                                                                             self.cleaned_data('zip_code'),
                                                                             exc_info=True, stack_info=True))

            raise forms.ValidationError('Something is wrong with that location!', code='invalid_location')

        # Compare these by zip code. We don't have an __eq__ operator overloaded
        if city_state_location.zip_code != zip_code_location.zip_code:
            logging.error('The zipcode returned from the client mapped to a different location than the raw city and'
                          'state returned from the client. \n'
                          'location_raw: {} \n'
                          'location matched with zip_code: {} \n'
                          'location matched with city and state: {}'.format(self.cleaned_data.get('location'),
                                                                            zip_code_location,
                                                                            city_state_location,
                                                                            exc_info=True, stack_info=True))
            forms.ValidationError('Something is wrong with that location!', code='invalid_location')

        self.cleaned_data['location'] = zip_code_location

        return

    def handle_datetime(self):
        #TODO this needs to be adjusted to handle timezones properly. We really need tp check start_date vs today after TZ conversion

        today = datetime.datetime.today()
        start_date = self.cleaned_data.get('start_date')

        # Ensure that the event date is not in the past
        #if start_date < today:
        #    logging.error('Event start date before current date')
        #    raise forms.ValidationError('The event date must be today or in the future', code='date_error')

        start_time = self.cleaned_data.get('start_time')

        inputted_datetime = datetime.datetime.combine(start_date, start_time)
        self.cleaned_data['start_datetime'] = inputted_datetime
        return

    def clean(self):
        self.handle_location()
        self.handle_datetime()

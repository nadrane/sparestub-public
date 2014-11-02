# Standard Imports
import logging
import datetime

#3rd Party Imports
from pytz import timezone as pytz_timezone
from haystack.forms import FacetedSearchForm

# Django Imports
from django import forms
from django.utils import timezone as dj_timezone


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

    start_date = forms.DateField(required=True)
    start_time = forms.TimeField(required=True,
                                 # Notice that we use %I instead of %H. This is so that the AM/PM affects the hour value.
                                 # https://docs.python.org/2/library/time.html#time.strftime
                                 input_formats=['%I:%M %p']
                                 )

    type = forms.ChoiceField(required=True,
                             choices=ticket_submit_form_settings.get('TICKET_TYPES'))

    payment_method = forms.ChoiceField(required=True,
                                       choices=ticket_submit_form_settings.get('PAYMENT_METHODS'))

    def handle_location(self):
        city, state = map(lambda x: x.strip().lower(), self.cleaned_data.get('location_raw').split(','))

        try:
            city_state_location = map_citystate_to_location(city, state)
        except LocationMatchingException as e:
            logging.error(e.msg + 'location_raw - {} did not match a location in the DB'
                          .format(self.cleaned_data.get('location_raw'),
                                  exc_info=True,
                                  stack_info=True,
                                  )
                         )

            raise forms.ValidationError('Something is wrong with that location!', code='invalid_location')

        self.cleaned_data['location'] = city_state_location
        return

    def handle_datetime(self):
        '''
        When Django accepts datetime input, it creates a datetime aware object relative to the current timezone.
        This current timezone will be the timezone of the user.
        When the user submits a ticket, we need to assign that ticket a datetime object that is tz aware in the timezone
        where the ticket event is located. This field makes sure that happens.

        This field expects to receive a list containing a formatted datetime string as well as a zipcode.
        The zipcode will be used to lookup the associated timezone.
        '''

        inputted_datetime = datetime.datetime.combine(self.cleaned_data.get('start_date'),
                                                      self.cleaned_data.get('start_time'))

        local_tz = pytz_timezone(self.cleaned_data.get('location').timezone)
        local_tz_aware_datetime = local_tz.localize(inputted_datetime)

        utc_tz = pytz_timezone('UTC')
        utc_tz_aware_datetime = utc_tz.normalize(local_tz_aware_datetime.astimezone(utc_tz))

        today = dj_timezone.now()  # Might as well keep seconds and microseconds in there so a time on now is accepted.
        if utc_tz_aware_datetime < today:
            logging.error('Event start date before current date')
            raise forms.ValidationError('Cannot submit ticket for event that has already started', code='expired_date')

        self.cleaned_data['start_datetime'] = utc_tz_aware_datetime
        return

    def clean(self):
        self.handle_location()
        self.handle_datetime()


class SearchTicketForm(FacetedSearchForm):
    search_query = forms.CharField(required=True)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(FacetedSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        return sqs
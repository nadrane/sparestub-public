# Standard Imports
import logging
import datetime

#3rd Party Imports
from pytz import timezone as pytz_timezone
from haystack.forms import FacetedSearchForm
from haystack.query import EmptySearchQuerySet

# Django Imports
from django import forms
from django.utils import timezone as dj_timezone

# SpareStub Imports
from .settings import ticket_submit_form_settings
from locations.models import map_citystate_to_location, LocationMatchingException
from utils.fields import CurrencyField


class SearchTicketForm(FacetedSearchForm):
    ticket_type = forms.ChoiceField(required=False,
                                    choices=ticket_submit_form_settings.get('TICKET_TYPES')
                                    )

    location_raw = forms.CharField(required=False,
                                   max_length=200
                                   )

    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

    def __init__(self, *args, **kwargs):
        super(SearchTicketForm, self).__init__(*args, **kwargs)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(SearchTicketForm, self).search()

        if not self.is_valid():
            return self.no_query_found()

        # If the default search returned an empty query set, it simply means that no query string q was entered.
        # There are other things we can search on, though, like location, dates, and ticket type.
        # Grab the original sqs filtered by is_active and ordered by date and filter over it.
        if isinstance(sqs, EmptySearchQuerySet):
            if self.cleaned_data['location_raw'] or self.cleaned_data['ticket_type'] or self.cleaned_data['start_date'] or self.cleaned_data['end_date']:
                sqs = self.searchqueryset
            else:
                # Default to new york if the user tries to search everywhere
                self.cleaned_data['location_raw'] = "New York, NY"
                sqs = self.searchqueryset

        # Check to see if a location was chosen. Make sure search results are from that location
        # TODO Make this location date sensitive and search nearby zip_codes
        # Should also filter down nearby city list to exclude zip codes that can never be chosen because they have
        # a city/state combo that has less population than another identical city/state combo
        if self.cleaned_data['location_raw']:

            # We might not get great input from the user. They might not have selected an autocomplete options.
            # If they didn't don't let this crash.
            try:
                location = self.get_location()
                if location:
                    sqs = sqs.filter(location=location)
            except forms.ValidationError:
                # If the location is not real, then clearly nothing can match the filters given.
                return EmptySearchQuerySet()

        if self.cleaned_data['ticket_type']:
            sqs = sqs.filter(ticket_type=self.cleaned_data.get('ticket_type'))

        if self.cleaned_data['start_date']:
            sqs = sqs.filter(start_date__gte=self.cleaned_data['start_date'])

        if self.cleaned_data['end_date']:
            sqs = sqs.filter(start_date__lte=self.cleaned_data['end_date'])

        return sqs

    def get_location(self):
        location_raw = self.cleaned_data.get('location_raw')
        city_state_location = None

        # Sometimes the user doesn't actually select an autocomplete option, and the input will not contain a comma.
        # This causes the unpacking to crash. Don't let that happen.
        if ',' in location_raw:
            city, state = map(lambda x: x.strip().lower(), location_raw.split(','))
        else:
            city, state = location_raw.strip().lower(), ''

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

        return city_state_location


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

    venue = forms.CharField(required=True,
                            max_length=ticket_submit_form_settings.get('VENUE_MAX_LENGTH')
                            )

    start_date = forms.DateField(required=True)
    start_time = forms.TimeField(required=True,
                                 # Notice that we use %I instead of %H. This is so that the AM/PM affects the hour value.
                                 # https://docs.python.org/2/library/time.html#time.strftime
                                 input_formats=['%I:%M %p']
                                 )

    ticket_type = forms.ChoiceField(required=True,
                                    choices=ticket_submit_form_settings.get('TICKET_TYPES'))

    # Disabling for lean launch
    #payment_method = forms.ChoiceField(required=True,
    #                                   choices=ticket_submit_form_settings.get('PAYMENT_METHODS'))

    def handle_location(self):
        location_raw = self.cleaned_data.get('location_raw')

        # Sometimes the user doesn't actually select an autocomplete option, and the input will not contain a comma.
        # This causes the unpacking to crash. Don't let that happen.
        if ',' in location_raw:
            city, state = map(lambda x: x.strip().lower(), location_raw.split(','))
        else:
            city, state = location_raw.strip().lower(), ''

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

        utc_tz_aware_datetime.replace(second=0, microsecond=0)  # We don't want to start sorting
                                                                # by time submitted accidentally
        self.cleaned_data['start_datetime'] = utc_tz_aware_datetime
        return

    def clean(self):
        self.handle_location()
        self.handle_datetime()
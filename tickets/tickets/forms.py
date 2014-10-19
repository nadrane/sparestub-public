# 3rd Party Modules
import requests
import logging
import json

# Django Imports
from django import forms

# SpareStub Imports
from .models import User
from .settings import ticket_form_settings
from locations.models import Location, Alias
from locations.settings import location_settings


#Form that will be displayed on signup.html to load a person
class TicketForm(forms.Form):
    price = forms.IntegerField(required=True)

    title = forms.CharField(required=True,
                            min_length=ticket_form_settings.get('TITLE_MAX_LENGTH'),
                            )

    city = forms.CharField(required=True)

    state = forms.ChoiceField(choices=location_settings.get('STATES'))

    start_timestamp = forms.DateTimeField(required=True)

    category = forms.ChoiceField(choices=ticket_form_settings.get('TICKET_TYPES'))

    def clean(self):
        '''
        We need to map the city and state to an entry in the location table.
        We should be able to do this pretty accurately using city and state. Note that there might be instances of
        two cities with the same name in the same state with different zipcodes.
        '''
        # Filter over states first because there's a far smaller chance the user selected the wrong state from the
        # select widget than the chance they fubbed the location name.
        possible_locations = Location.objects.filter(city=self.city)

        # When multiple cities map to the same zip code, all of location entries have the same latitude and longitude.
        # The choice to actually store the zip code in the 0th index is arbitrary.
        # We should NEVER look up tickets using another index other than ciy index. A zipcode lookup would yield
        # VERY incomplete results.
        if possible_locations:
            for location in possible_locations:
                if location.state == self.state:
                    # This is the location will we store in the DB
                    self.cleaned_data['location'] = location
                    return

        possible_locations = Alias.objects.filter(alias=self.city)

        if possible_locations:
            for location in possible_locations:
                if location.state == self.state:
                    # This is the location will we store in the DB
                    self.cleaned_data['location'] = location
                    return

        # If the entered city does not map to a zipcode, then the user entered an invalid location
        raise forms.ValidationError('Invalid location entered.', code='invalid_location')
# Standard Imports
import logging

# Django Imports
from django import forms

# SpareStub Imports
from .settings import ticket_submit_form_settings
from locations.models import Location, Alias, map_citystate_to_location, LocationMatchingException

#Form that will be displayed on signup.html to load a person
class SubmitTicketForm(forms.Form):
    price = forms.IntegerField(required=True)

    title = forms.CharField(required=True,
                            min_length=ticket_submit_form_settings.get('TITLE_MAX_LENGTH'),
                            )

    location_raw = forms.CharField(required=True)

    zip_code = forms.CharField(required=True)  # Not explicitly entered by the user but determined using the
                                               # city and state in location_raw

    start_datetimestamp = forms.DateTimeField(required=True)

    category = forms.ChoiceField(required=True,
                                 choices=ticket_submit_form_settings.get('TICKET_TYPES'))

    payment_method = forms.ChoiceField(required=True,
                                       choices=ticket_submit_form_settings.get('PAYMENT_METHODS'))

    def clean_start_timestamp(self):
        

    def clean_location(self):
        zip_code_location = Location.objects.filter(zip_code=self.cleaned_data.get('zip_code'))[0]
        if not zip_code_location:
            raise forms.ValidationError('Invalid zip code returned.', code='invalid_zip_code')

        city, state = map(lambda x: x.strip(), self.cleaned_data.get('location').split(','))

        try:
            city_state_location = map_citystate_to_location(city, state)
        except LocationMatchingException as e:
            logging.error(e.msg + 'location_raw: {} and zip_code: {}'.format(self.cleaned_data.get('location'),
                                                                             self.cleaned_data('zip_code'),
                                                                             exc_info=True, stack_info=True))


            raise forms.ValidationError('Something is wrong with that location!', code='invalid_location')

        if city_state_location != zip_code_location:
            logging.error('The zipcode returned from the client mapped to a different location than the raw city and'
                          'state returned from the client. \n'
                          'location_raw: {} \n'
                          'location matched with zip_code: {} \n'
                          'location matched with city and state: {}'.format(self.cleaned_data.get('location'),
                                                                            zip_code_location,
                                                                            city_state_location,
                                                                            exc_info=True, stack_info=True))
            forms.ValidationError('Something is wrong with that location!', code='invalid_location')


# Django Imports
from django import forms

# SpareStub Imports
from registration.settings import user_info_form_settings
from tickets.models import Ticket


class RequestToBuyForm(forms.Form):

    # The id of the ticket that the user is trying to buy
    ticket_id = forms.IntegerField(required=True)

    token = forms.CharField(required=True)

    email = forms.EmailField(required=True,
                             max_length=user_info_form_settings.get('EMAIL_MAX_LENGTH')
                             )

    def clean_ticket_id(self):
        """
        Ensure that the ticket that user is paying for exists.
        """

        try:
            ticket = Ticket.objects.get(pk=self.cleaned_data.get('ticket_id'))
        except Ticket.DoesNotExist:
            raise forms.ValidationError('Ticket does not exists', code='invalid_ticket')

        return self.cleaned_data.get('ticket_id')

    def clean_price(self):
        """
        Make sure that the price submitted is the same as the price of the ticket.
        """

        try:
            ticket = Ticket.objects.get(pk=self.cleaned_data.get('ticket_id'))
        except Ticket.DoesNotExist:
            raise forms.ValidationError('Ticket does not exists', code='invalid_ticket')

        if ticket.price != self.cleaned_data.get('price'):
            raise forms.ValidationError('User attempted to tamper with the ticket price', code='price_tampering')

        return self.cleaned_data.get('price')
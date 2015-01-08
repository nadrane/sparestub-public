# Django Imports
from django import forms
from django.core.exceptions import ObjectDoesNotExist

# SpareStub Imports
from .settings import send_message_form_settings
from tickets.models import Ticket
from registration.models import User

class SendMessageForm(forms.Form):
    body = forms.CharField(required=True,
                           max_length=send_message_form_settings.get('BODY_MAX_LENGTH'),
                           )

    # The id of the ticket to which this message refers
    ticket_id = forms.IntegerField(required=True)

    # The PK of the user that is being sent a message
    receiver_id = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SendMessageForm, self).__init__(*args, **kwargs)

    def clean_ticket_id(self):
        try:
            ticket = Ticket.objects.get(pk=self.cleaned_data.get('ticket_id'))
            self.cleaned_data['ticket'] = ticket
        except ObjectDoesNotExist:
            raise forms.ValidationError('This ticket does not exist!')

        if not ticket.is_active:
            raise forms.ValidationError('The poster of this ticket cancelled it in the last few minutes!')

        return self.cleaned_data.get('ticket_id')

    def clean_receiver_id(self):
        try:
            receiver = User.objects.get(pk=self.cleaned_data.get('receiver_id'))
            self.cleaned_data['receiver'] = receiver
        except ObjectDoesNotExist:
            raise forms.ValidationError('Something went wrong!')

        return self.cleaned_data.get('receiver_id')

    def clean(self):
        ticket_poster = self.cleaned_data.get('ticket').poster
        sender = self.request.user
        receiver = self.cleaned_data.get('receiver')

        # One of the users in the conversation better own the ticket
        if sender != ticket_poster and receiver != ticket_poster:
            raise forms.ValidationError("Something went wrong!")

        # A user cannot message themselves
        if sender == receiver:
            forms.ValidationError("Something went wrong!")


class MarkMessagesReadForm(forms.Form):
    ticket_id = forms.IntegerField(required=True)

    other_user_id = forms.IntegerField(required=True)
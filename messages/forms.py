# Django Imports
from django import forms
from django.core.exceptions import ObjectDoesNotExist

# SpareStub Imports
from tickets.models import Ticket
from registration.models import User

# Module Imports
from .settings import send_message_form_settings


class EditMessageForm(forms.Form):
    # The id of the ticket to which this message refers
    ticket_id = forms.IntegerField(required=True)

    # The PK of the user that is being sent a message
    other_user_id = forms.IntegerField(required=True)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EditMessageForm, self).__init__(*args, **kwargs)

    def clean_ticket_id(self):
        try:
            ticket = Ticket.objects.get(pk=self.cleaned_data.get('ticket_id'))
            self.cleaned_data['ticket'] = ticket
        except ObjectDoesNotExist:
            raise forms.ValidationError('This ticket does not exist!')

        if not ticket.is_active:
            raise forms.ValidationError('The poster of this ticket cancelled it in the last few minutes!')

        return self.cleaned_data.get('ticket_id')

    def clean_other_user_id(self):
        try:
            other_user = User.objects.get(pk=self.cleaned_data.get('other_user_id'))
            self.cleaned_data['other_user'] = other_user
        except ObjectDoesNotExist:
            raise forms.ValidationError('Something went wrong!')

        return self.cleaned_data.get('other_user_id')

    def clean(self):
        ticket_poster = self.cleaned_data.get('ticket').poster
        sender = self.request.user
        other_user = self.cleaned_data.get('other_user')

        # One of the users in the conversation better own the ticket
        if sender != ticket_poster and other_user != ticket_poster:
            raise forms.ValidationError("Something went wrong!")

        # A user cannot message themselves
        if sender == other_user:
            forms.ValidationError("Something went wrong!")


class SendMessageForm(EditMessageForm):

        body = forms.CharField(required=True,
                               max_length=send_message_form_settings.get('BODY_MAX_LENGTH'),
                               )

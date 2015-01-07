# Django Imports
from django import forms

# SpareStub Imports
from .settings import send_message_form_settings


class SendMessageForm(forms.Form):
    body = forms.CharField(required=True,
                           max_length=send_message_form_settings.get('BODY_MAX_LENGTH'),
                           )


class MarkMessagesReadForm(forms.Form):
    ticket_id = forms.IntegerField(required=True)

    other_user_id = forms.IntegerField(required=True)
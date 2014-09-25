# Django core modules
from django import forms

# Crowdsurfer imports
from .settings import contact_form_settings


class ContactForm(forms.Form):
    from_email_address = forms.EmailField(required=True)

    subject_type = forms.ChoiceField(required=True,
                                     choices=contact_form_settings['SUBJECT_TYPES'],
                                     widget=forms.Select
                                     )

    body = forms.CharField(required=True,
                           min_length=contact_form_settings['BODY_MINLENGTH'],
                           max_length=contact_form_settings['BODY_MAXLENGTH'],
                           widget=forms.Textarea,
                           )

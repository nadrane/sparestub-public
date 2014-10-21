# 3rd Party Modules
import requests
import logging
import json

# Django modules
from django import forms
from django.contrib.auth import authenticate
from django.forms import ValidationError

# Crowd Surfer

from .models import User
from utils.email import send_mail

from .settings import signup_form_settings, login_form_settings


#Form that will be displayed on signup.html to load a person
class SignupForm(forms.Form):

    email = forms.EmailField(required=True,
                             max_length=signup_form_settings['EMAIL_MAX_LENGTH'],
                             widget=forms.EmailInput(),
                             )

    password = forms.CharField(required=True,
                               min_length=signup_form_settings['PASSWORD_MIN_LENGTH'],
                               max_length=signup_form_settings['PASSWORD_MAX_LENGTH'],
                               widget=forms.PasswordInput(),
                               )

    first_name = forms.CharField(required=True,
                                 max_length=signup_form_settings['FIRST_NAME_MAX_LENGTH']
                                 )

    last_name = forms.CharField(required=True,
                                max_length=signup_form_settings['LAST_NAME_MAX_LENGTH']
                                )

    zipcode = forms.CharField(required=True,
                              max_length=signup_form_settings.get('ZIPCODE_MAX_LENGTH')
                              )

    #Make sure that this email address does not already exist in the database
    def clean_email(self):
        #TODO also check this on the front end via ajax
        return User.valid_email(self.cleaned_data.get('email', None))

    def clean_first_name(self):
        return User.valid_name(self.cleaned_data.get('first_name'))

    def clean_last_name(self):
        return User.valid_name(self.cleaned_data.get('last_name'))

    def clean_zipcode(self):
        return User.valid_zipcode(self.cleaned_data.get('zipcode'))


class LoginForm(forms.Form):
    '''
        This is the login form that is used in base.html and that always appears in the upper right hand corner of the
        page for users that are not logged in.
    '''

    email = forms.EmailField(max_length=login_form_settings['EMAIL_MAX_LENGTH'],
                             label='email',
                             widget=forms.EmailInput(attrs={'placeholder': 'Email'})
                             )
    
    password = forms.CharField(label='password',
                               widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
                               )

    def clean(self):
        # We know the form data is valid at this point. Log the user in.
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            if user.is_active:
                pass
            else:
                raise forms.ValidationError('This account has been disabled.', code="inactive_account")
        else:
            raise forms.ValidationError('Wrong email or password entered. Please try again.', code="invalid_credentials")

        return

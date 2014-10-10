__author__ = 'Nick'

# Django core modules
from django import forms

# Crowd Surfer modules
from registration.models import User
from registration.settings import user_model_settings
from .models import UserProfile


class EditUserProfileForm(forms.Form):

    email = forms.EmailField(required=True,
                             max_length=user_model_settings['EMAIL_MAX_LENGTH'],
                             widget=forms.EmailInput(),
                             )

    first_name = forms.CharField(max_length=user_model_settings['FIRST_NAME_MAX_LENGTH'],
                                 widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
                                 validators=[User.valid_name],
                                 )

    last_name = forms.CharField(max_length=user_model_settings['LAST_NAME_MAX_LENGTH'],
                                widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
                                validators=[User.valid_name],
                                )

    about = forms.CharField(required=False,
                            widget=forms.Textarea(attrs={'placeholder': 'Write a little bit about yourself...',
                                                         'maxlength': 500
                                                         }
                                                  )
                            )

    username = forms.CharField(required=True,
                               validators=[UserProfile.valid_username],
                               )

    website = forms.CharField(required=False)

    def clean_website(self):
        '''
        Validate that a correctly formatted URL was submitted. Place some restrictions on protocol.
        Return a slightly cleaner version of the url submitted. Strip of query parameters and add a protocol.
        '''
        return UserProfile.valid_website(self.cleaned_data['website'])

    def clean_email(self):
        '''
        Make sure that this email address does not already exist in the database
        '''
        return User.valid_email((self.cleaned_data['email']))


class PasswordChangeForm(forms.Form):

    current_password = forms.CharField(min_length=user_model_settings['PASSWORD_MIN_LENGTH'],
                                       max_length=user_model_settings['PASSWORD_MAX_LENGTH'],
                                       required=True,
                                       widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}),
                                       )

    new_password = forms.CharField(min_length=user_model_settings['PASSWORD_MIN_LENGTH'],
                                   max_length=user_model_settings['PASSWORD_MAX_LENGTH'],
                                   required=True,
                                   widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
                                   )

    confirm = forms.CharField(min_length=user_model_settings['PASSWORD_MIN_LENGTH'],
                              max_length=user_model_settings['PASSWORD_MAX_LENGTH'],
                              required=True,
                              widget=forms.PasswordInput(attrs={'placeholder': 'Confirm'}),
                              )

    def clean_current_password(self):
        if self.equal_to_current_password(self.cleaned_data['current_password']):
            forms.ValidationError('Your new password must be different than your old password.')

    def clean(self):
        new_password = self.cleaned_data['new_password']
        confirm = self.cleaned_data['confirm']

        if new_password and confirm and (new_password != confirm):
            raise forms.ValidationError('Password do not match. Please re-enter your new password.')
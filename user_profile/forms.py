# Django core modules
from django import forms

# SpareStub modules
from registration.forms import UserInfoForm
from .settings import edit_profile_form_settings


class EditProfileForm(UserInfoForm):

    username = forms.CharField(required=True,
                               max_length=edit_profile_form_settings.get('USERNAME_MAX_LENGTH')
                               )

    profile_picture = forms.ImageField(required=True)

    def clean_username(self):
        """
        Make sure that the submitted username is unique.
        """
        return self.request.user.user_profile.valid_username(self.cleaned_data.get('username'))

'''
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
'''
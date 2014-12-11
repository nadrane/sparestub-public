# Django Core Imports
from django import forms
from django.contrib.auth import authenticate
from django.forms import ValidationError

# SpareStub Imports
from .models import User
from .settings import user_info_form_settings, signup_form_settings, login_form_settings
from locations.models import Location
from utils.email import normalize_email

class UserInfoForm(forms.Form):
    email = forms.EmailField(required=True,
                             max_length=user_info_form_settings.get('EMAIL_MAX_LENGTH'),
                             widget=forms.EmailInput(),
                             )

    first_name = forms.CharField(required=True,
                                 max_length=user_info_form_settings.get('FIRST_NAME_MAX_LENGTH'),
                                 )

    last_name = forms.CharField(required=True,
                                max_length=user_info_form_settings.get('LAST_NAME_MAX_LENGTH'),
                                )

    birthdate = forms.DateField(required=True)

    zip_code = forms.CharField(required=True,
                               max_length=user_info_form_settings.get('ZIPCODE_MAX_LENGTH')
                               )

    def __init__(self, *args, **kwargs):
        """
        We override the __init__ method so that we have access to the request and ultimately the user object within
        the form's clean methods. The user object is needed when updating the user profile to compare the submitted
        user information to the old information.
        """
        self.request = kwargs.pop('request', None)
        super(UserInfoForm, self).__init__(*args, **kwargs)

    #Make sure that this email address does not already exist in the database
    def clean_email(self):
        return User.valid_email(self.cleaned_data.get('email', None), self.request.user)

    def clean_first_name(self):
        return User.valid_name(self.cleaned_data.get('first_name', ''))

    def clean_last_name(self):
        return User.valid_name(self.cleaned_data.get('last_name', ''))

    def clean_birthdate(self):
        return User.valid_birthdate(self.cleaned_data.get('birthdate', ''))

    def clean_zip_code(self):
        inputted_zip_code = Location.valid_zipcode(self.cleaned_data.get('zip_code'))

        #TODO is it okay for us to raise forms.ValidationError in here, or should we just return False?
        location = Location.objects.filter(zip_code=inputted_zip_code)[0]
        if not location:
            raise forms.ValidationError('Invalid zip code', code='invalid_zip_code')

        self.cleaned_data['location'] = location
        return inputted_zip_code


#Form that will be displayed on signup.html to load a person
class SignupForm(UserInfoForm):
    password = forms.CharField(required=True,
                               min_length=signup_form_settings['PASSWORD_MIN_LENGTH'],
                               max_length=signup_form_settings['PASSWORD_MAX_LENGTH'],
                               widget=forms.PasswordInput(),
                               )


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


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(max_length=login_form_settings['EMAIL_MAX_LENGTH'],
                             label='email',
                             )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = normalize_email(email)
        if not User.objects.filter(email=email):
            raise ValidationError('Email does not exist')
        return email
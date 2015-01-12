# Django core modules
from django import forms
from django.forms import ValidationError

# SpareStub modules
from registration.forms import UserInfoForm, ResetPasswordForm
from registration.settings import password_form_settings
from .settings import edit_profile_form_settings, profile_answer_form_settings


class ProfileAnswerForm(forms.Form):
    answer = forms.CharField(required=False,
                             max_length=profile_answer_form_settings.get('ANSWER_MAX_LENGTH'))


class EditProfileForm(UserInfoForm):

    username = forms.CharField(required=True,
                               max_length=edit_profile_form_settings.get('USERNAME_MAX_LENGTH')
                               )

    profile_picture = forms.ImageField(required=False)

    # Did the user change their profile picture or not?
    use_old_photo = forms.BooleanField(required=False,  # A boolean field cannot be required because an inputted value
                                                        # of False will cause it to fail every time.
                                       initial=False)

    # These are required when use_old_photo is false.
    # They are the coordinates of the cropped photo with respect to the inset in the edit profile activity.
    x = forms.IntegerField(required=False)   # Pixels from left side of image where crop begins
    y = forms.IntegerField(required=False)   # Pixels from top of image where crop begins
    w = forms.IntegerField(required=False)   # Height of crop
    h = forms.IntegerField(required=False)   # Width of crop

    rotate_degrees = forms.IntegerField(required=False,
                                        initial=0
                                        )

    def __init__(self, *args, **kwargs):
        if kwargs.get('request').FILES.get('profile_picture'):
            self.is_photo_blank = False
        else:
            self.is_photo_blank = True
        super(EditProfileForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        """
        Make sure that the submitted username is unique.
        """

        return self.request.user.user_profile.valid_username(self.cleaned_data.get('username'))

    def clean_rotate_degrees(self):
        rotate_degrees = self.cleaned_data.get('rotate_degrees', 0)

        # Handle the case where rotate_degrees is None. If the client passes up '', this will be the case
        if not rotate_degrees:
            rotate_degrees = 0

        rotate_degrees %= 360

        # The number of degrees rotated must be a multiple of 90
        if rotate_degrees % 90 != 0:
            raise ValidationError('Image was rotated {} degrees, which is not a multiple of 90'. format(rotate_degrees))
        return rotate_degrees

    def clean(self):

        #If we are not using the old photo, then the cropping coordinates must be present.
        if not self.cleaned_data.get('use_old_photo') and not self.is_photo_blank:
            # We need to >= in the case that x or y (actually it will be both) is equal to 0.
            # Default to -1 in case so the get method doesn't return None, resulting in python error. Fail gracefully.
            if not all(self.cleaned_data.get(attr, -1) >= 0 for attr in ['x', 'y', 'w', 'h']):
                raise ValidationError('The new photo submitted that was not cropped')

            # Make sure the the aspect ratio of the submitted photo is 1.
            if self.cleaned_data.get('w') != self.cleaned_data.get('h'):
                raise ValidationError('The aspect ratio of the new photo is not 1.')

        return


class ChangePasswordForm(ResetPasswordForm):

    current_password = forms.CharField(required=True,
                                       min_length=password_form_settings['PASSWORD_MIN_LENGTH'],
                                       max_length=password_form_settings['PASSWORD_MAX_LENGTH'],
                                       )

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')

        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        return self.request.user.password_correct(self.cleaned_data.get('current_password'))
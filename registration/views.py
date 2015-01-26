# Standard Imports
import json
import logging

# Django Core Imports
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.template.loader import render_to_string
from django.utils.timezone import activate
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.db import transaction
from django.contrib.auth.decorators import login_required

# SpareStub Imports
from .models import User, ForgotPasswordLink, EmailConfirmationLink
from .settings import signup_form_settings, login_form_settings, password_form_settings
from .forms import SignupForm, LoginForm, ResetPasswordForm, ForgotPasswordForm
from utils.networking import ajax_http, ajax_popup_notification, form_success_notification


def basic_info(request):
    return render(request,
                  'registration/basic_info.html',
                  )


def signup(request):
    #If the user is already logged in, they're doing something they aren't supposed to. Send them a 405.
    if request.user.is_authenticated():
        return HttpResponseNotAllowed(['POST'])

    # If the form has been submitted by the user
    if request.method == 'POST':
        signup_form = SignupForm(request.POST, request=request)
        #Determine which form the user submitted.
        if signup_form.is_valid():
            password = signup_form.cleaned_data.get('password')
            email = signup_form.cleaned_data.get('email')
            first_name = signup_form.cleaned_data.get('first_name')
            last_name = signup_form.cleaned_data.get('last_name')
            birthdate = signup_form.cleaned_data.get('birthdate')
            location = signup_form.cleaned_data.get('location')

            # Creates the user profile as well. Saves both objects to the database.
            User.objects.create_user(email=email,
                                     password=password,
                                     first_name=first_name,
                                     last_name=last_name,
                                     location=location,
                                     birthdate=birthdate,
                                     )

            return ajax_popup_notification('success', "One last step before you can log in! "
                                                      "We sent you a confirmation email that should "
                                                      "arrive in the next few minutes. "
                                                      "Just click the link inside. "
                                                      "Don't forget to check your spam folder too.",
                                           status=200)

        # If the user ignored out javascript validation and sent an invalid form, send back an error.
        # We don't actually specify what the form error was. This is okay because our app requires JS to be enabled.
        # If the user managed to send us an asynch request with JS disabled, they aren't using the site as designed.
        # eg., possibly a malicious user. No need to repeat the form pretty validation already done on the front end.
        else:
            return ajax_http(False, 400)

    # These need to go here instead of in the settings file to avoid circular dependencies
    signup_form_settings['ZIP_CODE_REMOTE_URL'] = reverse('valid_zip_code')
    signup_form_settings['EMAIL_REMOTE_URL'] = reverse('valid_email')

    return render(request,
                  'registration/signup.html',
                  {'form_settings': signup_form_settings})


def login(request):
    # If the user is already logged in, redirect him to the homepage
    if request.user.is_authenticated():
        return ajax_http({'isSuccessful': True,
                         'redirect_href': '/'},
                         )

    # If the form has been submitted by the user
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            # We actually do this authenticate function twice, once in LoginForm and once here.
            # The code is cleaner this way, despite the extra DB hits.
            user = authenticate(email=email, password=password)
            if not user.is_confirmed:
                EmailConfirmationLink.objects.create_email_confirmation(user)
                return ajax_http({'notification_type': 'alert-danger',
                                  'notification_content': 'You need to confirm your email address. We just sent you another link!'
                                  },
                                 status=400,
                                 )

            auth_login(request, user)
            activate(user.timezone())  # Configure time zone

            return ajax_http({'isSuccessful': True},
                             status=200,
                             request=request)
        else:
            return ajax_http({'notification_type': 'alert-danger',
                              'notification_content': 'Wrong username or password! <a href="{}">Click to reset your password</a>'
                              .format(reverse('create_forgot_password'))
                              },
                             status=400,
                             )

    return render(request,
                  'registration/login.html',
                  {'form_settings': login_form_settings})


def login_redirect(request):
    #If the user is already logged in, they're doing something they aren't supposed to. Send them a 405.
    if request.user.is_authenticated():
        return redirect('/')

    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            # We actually do this authenticate function twice, once in LoginForm and once here.
            # The code is cleaner this way, despite the extra DB hits.
            user = authenticate(email=email, password=password)
            auth_login(request, user)
            activate(user.timezone())  # Configure time zone
            return ajax_http({'redirect_href': '/'},
                             status=200
                             )
        else:
            return ajax_http({'notification_type': 'alert-danger',
                              'notification_content': render_to_string('user_profile/forgot_password.html',
                                                                       '',
                                                                       RequestContext(request))
                              },
                             status=400,
                             )

    return render(request,
                  'registration/login_redirect.html',
                  {'form_settings': login_form_settings})


def logout(request):
    auth_logout(request)

    # TODO This is going to need to redirect to the page the user was on, provided that page does not require authorization
    return HttpResponseRedirect('/')


def create_forgot_password(request):
    if request.method == 'POST':
        forgot_password_form = ForgotPasswordForm(request.POST)
        if forgot_password_form.is_valid():
            user = User.objects.filter(email=forgot_password_form.cleaned_data.get('email'))[0]
            ForgotPasswordLink.objects.create_forgot_password(user)
            return render(request,
                          'registration/forgot_password_email_sent.html')
        else:
            return render(request,
                          'registration/forgot_password.html',
                          {'bad_email': True}
                          )
    return render(request,
                  'registration/forgot_password.html')


@login_required
def create_email_confirmation_link(request):
    EmailConfirmationLink.objects.create_email_confirmation(request.user)
    return ajax_http(form_success_notification("An email is already on its way. Just click the link inside."))


def confirm_email(request, confirm_link):
    # Login is not required because only the user with the correc email address will ever know the confirmation url
    email_confirm_link = EmailConfirmationLink.objects.filter(link=confirm_link).filter(expired=False)
    if email_confirm_link:
        email_confirm_link = email_confirm_link[0]
        user = email_confirm_link.user
        email_confirm_link.expired = True
        user.is_confirmed = True

        with transaction.atomic():
            email_confirm_link.save()
            user.save()

        # Immediately log the user in after saving them to the database
        # Even though we know the user is valid because they clicked the confirmation link, we MUST authenticate anyway.
        # This is because authenticate sets an attribute on the user that notes that authentication was successful.
        # auth_login() requires this attribute to exist.
        # But we cannot authenticate the email with the password because don't know it, so we can use the confirm link
        # instead.
        user = authenticate(email_confirm_link=email_confirm_link)
        auth_login(request, user)
        activate(user.location.timezone)  # Configure time zone

        return render(request,
                      'registration/email_confirmation_finished.html')
    raise Http404()


def reset_password(request, reset_link):
    forgot_password_link = ForgotPasswordLink.objects.filter(link=reset_link).filter(expired=False)
    if forgot_password_link:
        if request.method == 'POST':
            reset_password_form = ResetPasswordForm(request.POST)
            if reset_password_form.is_valid():
                forgot_password_link = forgot_password_link[0]
                user = forgot_password_link.user
                email = user.email

                new_password = reset_password_form.cleaned_data.get('new_password')
                user.set_password(new_password)
                forgot_password_link.expired = True

                with transaction.atomic():
                    user.save()
                    forgot_password_link.save()

                user = authenticate(email=email, password=new_password)
                auth_login(request, user)
                return HttpResponseRedirect('/')
            else:
                return render(request,
                              'registration/reset_password.html',
                              {'reset_link': reset_link,
                               'bad_password': True,
                               'form_settings': password_form_settings
                               })
        return render(request,
                      'registration/reset_password.html',
                      {'reset_link': reset_link,
                       'form_settings': password_form_settings
                       })
    else:
        raise Http404()
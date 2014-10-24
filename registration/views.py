# Standard Imports
import json
import logging

# Django Core Imports
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.template.loader import render_to_string

# SpareStub Imports
from .models import User
from .settings import signup_form_settings, login_form_settings
from .forms import SignupForm, LoginForm
from utils.email import send_email
from utils.miscellaneous import get_variable_from_settings
from utils.networking import ajax_http
from .utils import render_nav_bar

SOCIAL_EMAIL_ADDRESS = get_variable_from_settings('SOCIAL_EMAIL_ADDRESS')


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
        signup_form = SignupForm(request.POST)
        #Determine which form the user submitted.
        if signup_form.is_valid():
            password = signup_form.cleaned_data.get('password')
            email = signup_form.cleaned_data.get('email')
            first_name = signup_form.cleaned_data.get('first_name')
            last_name = signup_form.cleaned_data.get('last_name')
            zipcode = signup_form.cleaned_data.get('zipcode')

            # Email the user to welcome them to out website.
            signup_email_message = render_to_string('registration/signup_email.html')
            send_email(email,
                       "Welcome to SpareStub!",
                       '',
                       SOCIAL_EMAIL_ADDRESS,
                       'SpareStub',
                       html=signup_email_message
                       )

            # Creates the user profile as well. Saves both objects to the database.
            new_user = User.objects.create_user(email=email,
                                                password=password,
                                                first_name=first_name,
                                                last_name=last_name,
                                                zipcode=zipcode,
                                                )

            #Immediately log the user in after saving them to the database
            #Even though we know the username_or_email and password are valid since we just got them, we MUST authenticate anyway.
            #This is because authenticate sets an attribute on the user that notes that authentication was successful.
            #auth_login() requires this attribute to exist.
            #Note that we pass in a non-hashed version of the password into authenticate
            user = authenticate(email=email, password=password)
            auth_login(request, user)

            return ajax_http(render_nav_bar, 200, request=request)

        # If the user ignored out javascript validation and sent an invalid form, send back an error.
        # We don't actually specify what the form error was. This is okay because our app requires JS to be enabled.
        # If the user managed to send us an aysynch request with JS disabled, they aren't using the site as designed.
        # eg., possibly a malicious user. No need to repeat the form pretty validation already done on the front end.
        else:
            return ajax_http(False, 400)

    return render(request,
                  'registration/signup.html',
                  {'form_settings': signup_form_settings})


def login(request):
    # If the user is already logged in, redirect him to the homepage
    if request.user.is_authenticated():
        return ajax_http(content='False',
                         status=400
                         )

    # If the user tried to access another page without logging in first, store that page here, and redirect them to it after login
    redirect_to_url = request.REQUEST.get('next', '')

    # If the form has been submitted by the user
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            # We actually do this authenticate function twice, once in LoginForm and once here.
            # The code is cleaner this way, despite the extra DB hits.
            user = authenticate(email=email, password=password)
            auth_login(request, user)
            return ajax_http(render_nav_bar, 200, request=request)
        else:
            return ajax_http({'isSuccessful': False,
                              'notification_type': 'alert-danger',
                              'notification_content': 'Wrong username or password!'
                              },
                             status=400
                             )

    return render(request,
                  'registration/login.html',
                  {'form_settings': login_form_settings})

def logout(request):
    auth_logout(request)

    # TODO This is going to need to redirect to the page the user was on, provided that page does not require authorization
    return HttpResponseRedirect('/')


def email_valid(request):
    '''
    Used during form validation to verify that an inputted email address has not been used.
    '''

    if request.method == 'GET':
        email = request.GET.get('email')
        return HttpResponse(json.dumps(User.valid_email(email)))
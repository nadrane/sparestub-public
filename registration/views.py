# Core Modules
import json
import logging

# Django core modules
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.decorators import login_required

# SpareStub modules
#from .models import User
from .settings import signup_form_settings, login_form_settings
#from .forms import SignupForm, LoginForm
#from .utils import after_AJAX_login_HTTP_response


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
            email = signup_form.cleaned_data.get('email', None) # Not always sent if user signs up with Facebook
                                                    # that does not have a released email.
            first_name = signup_form.cleaned_data.get('first_name')
            last_name = signup_form.cleaned_data.get('last_name')
            fb_uid = signup_form.cleaned_data.get('fb_uid', None)  # Not always sent. Default to none if user signed up with email.

            # This should never happen. Form validation should prevent it.
            if not email and not fb_uid:
                logger = logging.error('User created without email or facebook ID.')
                return form_default_HTTP_response_redirect()

            #Email the user to welcome them to out website.  Do this before creating a user in case there are errors.
            #send_mail('Welcome!', message, "DatingWebsite.com", [form.cleaned_data['email']])

            #Check to see if this username_or_email already exists in the database... Probably best down with an
            #AJAX query immediately after inputting the username_or_email

            new_user = User.objects.create_user(email=email,
                                                password=password,
                                                first_name=first_name,
                                                last_name=last_name,
                                                facebook_user_id=fb_uid,
                                                )

            #Immediately log the user in after saving them to the database
            #Even though we know the username_or_email and password are valid since we just got them, we MUST authenticate anyway.
            #This is because authenticate sets an attribute on the user that notes that authentication was successful.
            #auth_login() requires this attribute to exist.
            #Note that we pass in a non-hashed version of the password into authenticate
            user = authenticate(email=email, password=password)
            auth_login(request, user)

            return after_AJAX_login_HTTP_response(request, user)
    else:
        signup_form = SignupForm()

    return render(request,
                  'registration/signup.html',
                  {'is_form_bound': signup_form.is_bound,
                   'errors': signup_form.errors,
                   'non_field_errors': signup_form.non_field_errors,
                   'form_settings': signup_form_settings,
                   },
                  )


def login(request):
    return

"""
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
            email = signup_form.cleaned_data.get('email', None) # Not always sent if user signs up with Facebook
                                                    # that does not have a released email.
            first_name = signup_form.cleaned_data.get('first_name')
            last_name = signup_form.cleaned_data.get('last_name')
            fb_uid = signup_form.cleaned_data.get('fb_uid', None)  # Not always sent. Default to none if user signed up with email.

            # This should never happen. Form validation should prevent it.
            if not email and not fb_uid:
                logger = logging.error('User created without email or facebook ID.')
                return form_default_HTTP_response_redirect()

            #Email the user to welcome them to out website.  Do this before creating a user in case there are errors.
            #send_mail('Welcome!', message, "DatingWebsite.com", [form.cleaned_data['email']])

            #Check to see if this username_or_email already exists in the database... Probably best down with an
            #AJAX query immediately after inputting the username_or_email

            new_user = User.objects.create_user(email=email,
                                                password=password,
                                                first_name=first_name,
                                                last_name=last_name,
                                                facebook_user_id=fb_uid,
                                                )

            #Immediately log the user in after saving them to the database
            #Even though we know the username_or_email and password are valid since we just got them, we MUST authenticate anyway.
            #This is because authenticate sets an attribute on the user that notes that authentication was successful.
            #auth_login() requires this attribute to exist.
            #Note that we pass in a non-hashed version of the password into authenticate
            user = authenticate(email=email, password=password)
            auth_login(request, user)

            return after_AJAX_login_HTTP_response(request, user)
    else:
        signup_form = SignupForm()

    return render(request,
                  'registration/signup.html',
                  {'is_form_bound': signup_form.is_bound,
                   'errors': signup_form.errors,
                   'non_field_errors': signup_form.non_field_errors,
                   'form_settings': signup_form_settings,
                   },
                  )


def logout(request):
    auth_logout(request)

    # TODO This is going to need to redirect to the page the user was on, provided that page does not require authorization
    return HttpResponseRedirect('/')


def login(request):
    # If the user is already logged in, redirect him to the homepage
    if request.user.is_authenticated():
        return HttpResponseForbidden(content='Already logged in')

    # If the user tried to access another page without logging in first, store that page here, and redirect them to it after login
    redirect_to_url = request.REQUEST.get('next', '')
    if redirect_to_url:
        pass
        #TODO not really sure how to handle these since everything takes place from the main page.

    # If the form has been submitted by the user
    if request.method == 'POST':
        # If the user logged in via facebook
        if 'fb_uid' in request.POST:
            return facebook_login(request)
        #If the user logged in via email
        else:
            return email_login(request)
    else:
        login_form = LoginForm()

    return render(request,
                  'registration/login.html',
                  {'login_form': login_form,
                   'form_settings': login_form_settings,
                   }
                  )


def email_login(request):
    login_form = LoginForm(request.POST)
    if login_form.is_valid():
        email = request.POST['email']
        password = request.POST['password']
        # We actually do this authenticate function twice, once in LoginForm and once here.
        # The code is cleaner this way, despite the extra DB hits.
        user = authenticate(email=email, password=password)
        auth_login(request, user)
        return after_AJAX_login_HTTP_response(request, user)
    else:
        login_form = LoginForm()
    return render(request,
                  'registration/login.html',
                  {'login_form': login_form,
                   'form_settings': login_form_settings,
                   }
    )


def facebook_login(request):
    json_response = {}

    fb_uid = request.POST.get('fb_uid', None)  # Unique ID FB uses to identify it's members
    fb_access_token = request.POST.get('fb_access_token', None)
    login_form_active_onscreen = request.POST.get('login_form_active_onscreen', None)  # (boolean) Is the login modal form currently visible?
    is_signup_form_loaded = request.POST.get('is_signup_form_loaded', None)  # (boolean) Has the signup form been sent to the client already?

    # This isn't actually json (it's just post parameter data), so don't use json.loads.
    if login_form_active_onscreen == 'true':
        login_form_active_onscreen = True
    elif login_form_active_onscreen == 'false':
        login_form_active_onscreen = False
    else:
        login_form_active_onscreen = None

    if is_signup_form_loaded == 'true':
        is_signup_form_loaded = True
    elif is_signup_form_loaded == 'false':
        is_signup_form_loaded = False
    else:
        is_signup_form_loaded = None


    #Is this an existing user in our database or a new account?
    user = authenticate(fb_uid=fb_uid, fb_access_token=fb_access_token)
    if user:
        json_response["new_user"] = False
        auth_login(request, user)
        # Simply render the homepage and redirect the user on the client side. Remember this is an async request
        response = form_default_HTTP_response_redirect(request)

    else:
        json_response['new_user'] = True
        # Only send the signup form if the user specifically tried to login to FB
        # and if it has never been sent before
        if login_form_active_onscreen and not is_signup_form_loaded:
            signup_form = SignupForm()
            json_response['signup_form_html'] = render(request,
                                                       'registration/signup.html',
                                                       {'signup_form': signup_form}
                                                       )
            # render.content will give us a byte literal string. We need to decode it so that json.dumps knows what's going on.
            json_response['signup_form_html'] = json_response['signup_form_html'].content.decode('utf-8')


            response = HttpResponse(json.dumps(json_response),
                                    content_type='application/json'
                                    )
    return response

@login_required
def basic_info(request):
    #Grab the user who submitted the request. We will populate the form with their data.
    user = request.user

    # If the form has been submitted by the user
    if request.method == 'POST':
        form = BasicInfoForm(data=request.POST)
        if form.is_valid():
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.person.about = form.cleaned_data['about']

            user.person.save(force_update=True)

            #We will never be creating new members here, only updating existing ones
            user.save(force_update=True)

            return HttpResponseRedirect('/profile.html/basic_info')

    #We want to populate the form with the most up to date information regardless of whether a GET or POST came.
    #That is, we do not care if the user information was just updated.
    email = user.email
    # TODO convert name to title case
    first_name = user.first_name
    about = user.person.about
    birth_date = user.person.birth_date

    form = BasicInfoForm(initial={'email': email, 'first_name': first_name, 'about': about, 'birth date': birth_date})

    #context_instance is needed for the CSRF token.
    return render(request,
                  'basic_info.html',
                  {'form': form, },
                  context_instance=RequestContext(request)
    )

    #TODO - Implement me


@login_required
def settings(request):
    form = SettingsForm()
    return render(request,
                  'settings.html',
                  {'form': form, },
                  context_instance=RequestContext(request)
    )


def delete_photo(request):
    if request.method == 'POST':
        clickedPhotoId = request.POST['photo']

        photoToDelete = Photo.objects.get(pk=clickedPhotoId)

        #Note that the delete method of Photo is overridden, and the actual files (in addition to the DB entries) will be deleted from the server
        photoToDelete.delete()

        return HttpResponse("true")


def check_duplicate_email(request):
    if request.is_ajax():
        requester = request.user
        #Make sure that this email address does not already exist in the database
        #Even though the database only contains lowercase names, consider case-sensitivity.  Just as an extra error check
        try:
            userWithEmail = Person.objects.filter(user__email__iexact=request.GET['email'])[0].user
            ##But we do not want an error to fire if the user simply enters the profile.html but does not change his email address.
            if userWithEmail == requester:
                return HttpResponse("true")
            else:
                return HttpResponse("false")

        except IndexError:
            return HttpResponse("true")

    return HttpResponse("false")


def check_duplicate_username(request):
    if request.is_ajax():
        #Make sure that this username does not already exist in the database
        #even though the database only contains lowercase emails, consider case-sensitivity.  Just as an extra error check
        if Person.objects.filter(user__username=request.GET['username']):
            return HttpResponse(json.dumps(False))
        return HttpResponse(json.dumps(True))

    return HttpResponse("false")


def search_users(request):
    if request.is_ajax():
        searchString = request.GET['searchString']
        context = request.GET['context']

        if context == messages:
            userList = lookup_by_name(searchString)"""
# Standard Imports
import logging

# Django Imports
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# SpareStub Imports
from user_profile.models import UserProfile, ProfileQuestion, ProfileAnswer
from reviews.models import Review
from tickets.models import Ticket
from .forms import EditProfileForm, ProfileAnswerForm, ChangePasswordForm
from .settings import edit_profile_form_settings, profile_answer_form_settings
from registration.settings import password_form_settings
from utils.networking import ajax_http, form_failure_notification, \
    form_success_notification
from photos.models import Photo
from asks.models import Request


def edit_profile(request, username):
    profile = UserProfile.get_user_profile_from_username(username)
    # Make sure that the profile exists

    if profile:
        user = profile.user
    else:
        raise Http404('The username {} does not exist'.format(username))

    # Make sure that a user is only able to update his profile and nobody else's.
    if request.user != user:
        raise Http404('Uh oh! Something went wrong!')

    if request.method == 'POST':
        edit_profile_form = EditProfileForm(request.POST, request.FILES, request=request)
        #Determine which form the user submitted.
        if edit_profile_form.is_valid():
            user = request.user

            use_old_photo = edit_profile_form.cleaned_data.get('use_old_photo')

            if not use_old_photo:

                # Check to see if there is an existing photo and delete it if there is. This will delete it from S3
                try:
                    profile_picture = user.profile_picture
                    profile_picture.delete()
                except ObjectDoesNotExist:
                    pass

                uploaded_photo = request.FILES.get('profile_picture')
                if uploaded_photo:
                    x, y = edit_profile_form.cleaned_data.get('x'), edit_profile_form.cleaned_data.get('y'),
                    x2, y2 = x + edit_profile_form.cleaned_data.get('w'), y + edit_profile_form.cleaned_data.get('h')
                    crop_coords = x, y, x2, y2
                    rotate_degrees = edit_profile_form.cleaned_data.get('rotate_degrees', 0)
                    profile_picture = Photo.objects.create_photo(user, uploaded_photo, crop_coords, rotate_degrees)
                else:
                    profile_picture = None
            else:
                profile_picture = None

            email = edit_profile_form.cleaned_data.get('email')
            first_name = edit_profile_form.cleaned_data.get('first_name')
            last_name = edit_profile_form.cleaned_data.get('last_name')
            username = edit_profile_form.cleaned_data.get('username')
            location = edit_profile_form.cleaned_data.get('location')

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.location = location

            # No need to handle the profile picture if we are using the old one.
            if profile_picture:
                profile_picture.save()
                user.save()
            else:
                user.save()


            user.user_profile.username = username
            user.user_profile.save()

            return redirect(reverse('view_profile', kwargs={'username': username}))
        else:
            raise Http404()

    # We cannot put this line of code in the settings file which so many things are dependent on.
    # It raises circular dependency hell because it calls into all of the urls.py modules and consequently all of
    # the views.py modules.
    edit_profile_form_settings['ZIP_CODE_REMOTE_URL'] = reverse('valid_zip_code')
    edit_profile_form_settings['USERNAME_REMOTE_URL'] = reverse('valid_username')
    edit_profile_form_settings['EMAIL_REMOTE_URL'] = reverse('valid_email')
    edit_profile_form_settings['PASSWORD_REMOTE_URL'] = reverse('correct_password')

    edit_profile_form_settings.update(password_form_settings)

    return render(request,
                  'user_profile/edit_profile.html',
                  {'form_settings': edit_profile_form_settings,
                   'user_info': user
                   }
                  )


def view_profile(request, username):
    # Look up the user record who corresponds to this profile
    profile = UserProfile.get_user_profile_from_username(username)
    if profile:
        user = profile.user
    else:
        raise Http404('The username {} does not exist'.format(username))

    # If the user looking at this profile is its owner, then we want to render a couple edit buttons
    if request.user == user:
        is_owner = True
    else:
        is_owner = False

    user_location = user.location

    most_recent_review = user.most_recent_review()

    user_info = {'name': user,
                 'age': user.age(),
                 'city': user_location.city,
                 'state': user_location.state,
                 'rating': user.rating,
                 'username': username,
                 }

    try:
        user_info['profile_picture'] = user.profile_picture
    except ObjectDoesNotExist:
        pass

    if most_recent_review:
        reviewer_location = most_recent_review.reviewer.location
        reviewer_city, reviewer_state = reviewer_location.city, reviewer_location.state
        most_recent_review_info = {'name': most_recent_review.reviewer.get_short_name(),
                                   'age': most_recent_review.reviewer.age(),
                                   'city': reviewer_city,
                                   'state': reviewer_state,
                                   'contents': most_recent_review.contents,
                                   'rating': most_recent_review.rating
                                   }
    else:
        most_recent_review_info = None

    # Get the profile questions and the user's answers, if they exist.
    profile_questions = ProfileQuestion.objects.all()
    question_answer_pairs = ((ProfileAnswer.get_answer(user, profile_question), profile_question)
                             for profile_question in profile_questions)

    return render(request,
                  'user_profile/view_profile.html',
                  {'user_info': user_info,
                   'is_owner': is_owner,
                   'question_answer_pairs': question_answer_pairs,
                   'most_recent_review_info': most_recent_review_info,
                   'form_settings': profile_answer_form_settings,
                   },
                  content_type='text/html',
                  )


def profile_reviews(request, username):
    # Look up the user record who corresponds to this profile
    profile = UserProfile.get_user_profile_from_username(username)
    if profile:
        user = profile.user
    else:
        raise Http404('The username {} does not exist'.format(username))

    # If the user looking at this profile is its owner, then we want to render a couple edit buttons
    if request.user == user:
        is_owner = True
    else:
        is_owner = False

    user_location = user.location

    user_info = {'name': user,
                 'age': user.age(),
                 'city': user_location.city,
                 'state': user_location.state,
                 'rating': user.rating,
                 'username': username,
                 }

    try:
        user_info['profile_picture'] = user.profile_picture
    except ObjectDoesNotExist:
        pass

    reviews = Review.objects.filter(reviewee=user.id).order_by('creation_timestamp')

    if reviews:
        most_recent_review = reviews[0]
        reviewer_location = most_recent_review.reviewer.location
        reviewer_city, reviewer_state = reviewer_location.city, reviewer_location.state
        most_recent_review_info = {'name': most_recent_review.reviewer.get_short_name(),
                                   'age': most_recent_review.reviewer.age(),
                                   'city': reviewer_city,
                                   'state': reviewer_state,
                                   'contents': most_recent_review.contents,
                                   'rating': most_recent_review.rating
                                   }
    else:
        most_recent_review_info = None

    return render(request,
                  'user_profile/profile_reviews.html',
                  {'user_info': user_info,
                   'is_owner': is_owner,
                   'most_recent_review_info': most_recent_review_info,
                   'reviews': reviews,
                   'form_settings': profile_answer_form_settings,
                   },
                  content_type='text/html',
                  )


def profile_tickets(request, username):
    # Look up the user record who corresponds to this profile
    profile = UserProfile.get_user_profile_from_username(username)
    if profile:
        user = profile.user
    else:
        raise Http404('The username {} does not exist'.format(username))

    # If the user looking at this profile is its owner, then we want to render a couple edit buttons
    if request.user == user:
        is_owner = True
    else:
        is_owner = False

    user_location = user.location

    most_recent_review = user.most_recent_review()

    user_info = {'name': user,
                 'age': user.age(),
                 'city': user_location.city,
                 'state': user_location.state,
                 'rating': user.rating,
                 'username': username,
                 }

    try:
        user_info['profile_picture'] = user.profile_picture
    except ObjectDoesNotExist:
        pass

    if most_recent_review:
        reviewer_location = most_recent_review.reviewer.location
        reviewer_city, reviewer_state = reviewer_location.city, reviewer_location.state
        most_recent_review_info = {'name': most_recent_review.reviewer.get_short_name(),
                                   'age': most_recent_review.reviewer.age(),
                                   'city': reviewer_city,
                                   'state': reviewer_state,
                                   'contents': most_recent_review.contents,
                                   'rating': most_recent_review.rating
                                   }
    else:
        most_recent_review_info = None

    # Grab every ticket that this user has posted or has bid on
    upcoming_tickets = Ticket.upcoming_tickets(user)
    available_tickets = Ticket.available_tickets(user)
    in_progress_tickets = Ticket.in_progress_ticket(user)
    past_tickets = Ticket.past_tickets(user)

    return render(request,
                  'user_profile/profile_tickets.html',
                  {'user_info': user_info,
                   'is_owner': is_owner,
                   'upcoming_tickets': upcoming_tickets,
                   'available_tickets': available_tickets,
                   'in_progress_tickets': in_progress_tickets,
                   'past_tickets': past_tickets,
                   'most_recent_review_info': most_recent_review_info,
                   'form_settings': profile_answer_form_settings,
                   },
                  content_type='text/html',
                  )


def view_ticket(request, username, ticket_id):
    """
    View the details for a particular ticket. This view allows us to message the user or buy the ticket from him.
    """
    user = request.user

     # Look up the user record who corresponds to this profile
    profile = UserProfile.get_user_profile_from_username(username)
    if profile:
        profile_user = profile.user
    else:
        raise Http404('The username {} does not exist.'.format(username))

    # Make sure that ticket exists
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404()

    # Make sure that the username entered is the actual poster of this ticket
    if ticket.poster != profile_user:
        raise Http404('{} did not post that ticket.'.format(profile_user.user_profile.username))

    if not ticket.can_view():
        raise Http404('It looks like this page no longer exists. The user probably cancelled their ticket.')

    # If the user looking at this profile is its owner, then we want to render a couple edit buttons
    if user == profile_user:
        is_owner = True
    else:
        is_owner = False

    user_location = profile_user.location

    most_recent_review = profile_user.most_recent_review()

    user_info = {'name': profile_user,
                 'age': profile_user.age(),
                 'city': user_location.city,
                 'state': user_location.state,
                 'rating': profile_user.rating,
                 'username': username,
                 'user_id': profile_user.id,
                 'email': profile_user.email
                 }

    try:
        user_info['profile_picture'] = profile_user.profile_picture
    except ObjectDoesNotExist:
        pass

    if most_recent_review:
        reviewer_location = most_recent_review.reviewer.location
        reviewer_city, reviewer_state = reviewer_location.city, reviewer_location.state
        most_recent_review_info = {'name': most_recent_review.reviewer.get_short_name(),
                                   'age': most_recent_review.reviewer.age(),
                                   'city': reviewer_city,
                                   'state': reviewer_state,
                                   'contents': most_recent_review.contents,
                                   'rating': most_recent_review.rating
                                   }
    else:
        most_recent_review_info = None

    return render(request,
                  'user_profile/view_ticket.html',
                  {'user_info': user_info,
                   'is_owner': is_owner,
                   'ticket': ticket,
                   'most_recent_review_info': most_recent_review_info,
                   'stripe_public_api_key': settings.STRIPE_PUBLIC_API_KEY,
                   'has_request': Request.has_requested(ticket, user.id), # We pass in user.id because otherwise the
                                                                          # if the user is anonymous, it would be a
                                                                          # SimpleLazyObject, and Django would error out
                   'ticket_status': ticket.status,
                   },
                  content_type='text/html',
                  )


def update_question(request, username, question_id):
    """
    Update a single answer for a particular profile question of a particular user
    """
    profile = UserProfile.get_user_profile_from_username(username)
    # Make sure that the profile exists
    if profile:
        user = profile.user
    else:
        return form_failure_notification('User does not exist')

    # Make sure that a user is only able to update his profile and nobody else's.
    if request.user != user:
        return form_failure_notification('Uh oh! Something went wrong!')

    if request.method == 'POST':
        profile_answer_form = ProfileAnswerForm(request.POST)
        if profile_answer_form.is_valid():
            new_answer = request.POST.get('answer', '')

            profile_answer = ProfileAnswer.get_answer(user, ProfileQuestion.objects.get(id=question_id))
            profile_answer.answer = new_answer
            profile_answer.save()
            return ajax_http(form_success_notification('Question successfully updated'))
        else:
            return ajax_http(form_failure_notification('Answer too long'))


def change_password(request, username):
    if request.method == 'POST':
        profile = UserProfile.get_user_profile_from_username(username)
        # Make sure that the profile exists
        if profile:
            user = profile.user
        else:
            raise Http404('The username {} does not exist'.format(username))

        # Make sure that a user is only able to update his profile and nobody else's.
        if request.user != user:
            raise Http404('')

        change_password_form = ChangePasswordForm(request.POST, request=request)

        if change_password_form.is_valid():
            new_password = change_password_form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            return redirect(reverse('view_profile', kwargs={'username': username}))
        else:
            raise Http404()
    raise Http404()


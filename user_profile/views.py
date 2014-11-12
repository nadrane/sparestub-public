# Django Imports
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect
from django.http import Http404
from django.db.models import Q

# SpareStub Imports
from user_profile.models import UserProfile, ProfileQuestion, ProfileAnswer
from reviews.models import Review
from tickets.models import Ticket
from .forms import EditProfileForm, ProfileAnswerForm
from .settings import edit_profile_form_settings, profile_answer_form_settings
from utils.networking import ajax_http, non_field_errors_notification, form_failure_notification, \
    form_success_notification
from photos.models import Photo


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

            uploaded_photo = request.FILES.get('profile_picture')

            if uploaded_photo:
                profile_picture = Photo.objects.create_photo(uploaded_photo)

                user.profile_picture = profile_picture

            email = edit_profile_form.cleaned_data.get('email')
            first_name = edit_profile_form.cleaned_data.get('first_name')
            last_name = edit_profile_form.cleaned_data.get('last_name')
            username = edit_profile_form.cleaned_data.get('username')
            location = edit_profile_form.cleaned_data.get('location')

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.location = location

            # Make sure the picture does not get saved without first attaching it to a profile.
            # It would be lost be good otherwise.
            with transaction.atomic():
                profile_picture.save()
                user.profile_picture = profile_picture
                user.save()


            user.user_profile.username = username
            user.user_profile.save()

            return redirect(reverse('view_profile', kwargs={'username': username}))
        else:
            return ajax_http(**non_field_errors_notification(edit_profile_form))

    # We cannot put this line of code in the settings file which so many things are dependent on.
    # It raises circular dependency hell because it calls into all of the urls.py modules and consequently all of
    # the views.py modules.
    edit_profile_form_settings['ZIP_CODE_REMOTE_URL'] = reverse('valid_zip_code')
    edit_profile_form_settings['USERNAME_REMOTE_URL'] = reverse('valid_username')
    edit_profile_form_settings['EMAIL_REMOTE_URL'] = reverse('valid_email')

    return render(request,
                  'user_profile/edit_profile.html',
                  {'form_settings': edit_profile_form_settings}
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

    if user.profile_picture:
        user_info['profile_picture'] = user.profile_picture

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

    if user.profile_picture:
        user_info['profile_picture'] = user.profile_picture

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

    if user.profile_picture:
        user_info['profile_picture'] = user.profile_picture

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
    available_tickets = Ticket.objects.filter(poster=user, is_active=True)
    in_progress_tickets = Ticket.objects.filter(bidders=user, is_active=True)
    past_tickets = Ticket.objects.filter(Q(poster=user) | Q(bidders=user)).filter(is_active=False)

    return render(request,
                  'user_profile/profile_tickets.html',
                   {'user_info': user_info,
                    'is_owner': is_owner,
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
    import pdb
    pdb.set_trace()

     # Look up the user record who corresponds to this profile
    profile = UserProfile.get_user_profile_from_username(username)
    if profile:
        user = profile.user
    else:
        raise Http404('The username {} does not exist'.format(username))

    ticket = Ticket.objects.get(pk=ticket_id)
    # Make sure that the username entered is the actual poster of this ticket
    if not ticket or ticket.poster != user:
        raise Http404('That ticket does not exist for this user')

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

    if user.profile_picture:
        user_info['profile_picture'] = user.profile_picture

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
                  'user_profile/profile_tickets.html',
                  {'user_info': user_info,
                   'is_owner': is_owner,
                   'ticket': ticket,
                   'most_recent_review_info': most_recent_review_info,
                   'form_settings': profile_answer_form_settings,
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




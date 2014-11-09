# Django Imports
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db import transaction

# SpareStub Imports
from user_profile.models import UserProfile, ProfileQuestion, ProfileAnswer
from reviews.models import Review
from tickets.models import Ticket
from .forms import EditProfileForm
from .settings import edit_profile_form_settings
from utils.networking import ajax_http, non_field_errors_notification, form_failure_notification
from photos.models import Photo, convert_image_string


def edit_profile(request, username):
    # Make sure that a user is only able to update his profile and nobody else's.
    if request.user != UserProfile.get_user_profile_from_username(username).user:
        return form_failure_notification('Uh oh! Something went wrong!')

    if request.method == 'POST':
        edit_profile_form = EditProfileForm(request.POST, request.FILES, request=request)
        #Determine which form the user submitted.
        import pdb
        pdb.set_trace()
        if edit_profile_form.is_valid():
            user = request.user

            profile_picture = request.FILES.get('profile_picture')

            if profile_picture:
                original_file, profile_thumbnail_file, search_thumbnail_file = convert_image_string(profile_picture)

                profile_picture = Photo(original_file=original_file,
                                        search_thumbnail=search_thumbnail_file,
                                        profile_thumbnail=profile_thumbnail_file,
                                        )
                # We need to photo to be associated with a user profile, otherwise it will be lost forever
                # Make sure these two operations happen together.
                with transaction.atomic():
                    profile_picture.save()
                    user.user_profile.profile_picture = profile_picture
                    user.user_profile.save()


            email = edit_profile_form.cleaned_data.get('email')
            first_name = edit_profile_form.cleaned_data.get('first_name')
            last_name = edit_profile_form.cleaned_data.get('last_name')
            username = edit_profile_form.cleaned_data.get('username')
            location = edit_profile_form.cleaned_data.get('location')

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.location = location
            user.save()

            user.user_profile.username = username
            user.user_profile.save()

            return ajax_http(True,
                             extra_json={'is_redirect': True,
                                         'redirect_href': reverse('view_profile', kwargs={'username': username})}
                             )
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
    user = UserProfile.get_user_profile_from_username(username).user

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
                 'rating': range(user.rating)  # Django templates don't support ranges,
                                               # so much sure we have an iterable list here
                 }

    if most_recent_review:
        reviewer_location = most_recent_review.reviewer.location
        reviewer_city, reviewer_state = reviewer_location.city, reviewer_location.state
        most_recent_review_info = {'name': most_recent_review.reviewer.get_short_name(),
                                   'age': most_recent_review.reviewer.age(),
                                   'city': reviewer_city,
                                   'state': reviewer_state,
                                   'contents': most_recent_review.contents,
                                   'rating': range(most_recent_review.rating)  # Django templates don't support ranges,
                                                                               # so much sure we have an iterable list
                                                                               # here
                                   }
    else:
        most_recent_review_info = None

    # Get the profile questions and the user's answers, if they exist.
    profile_questions = ProfileQuestion.objects.all()
    question_answer_pairs = [(ProfileAnswer.get_answer(user, question), question)
                             for question in profile_questions]
    return render(request,
                  'user_profile/view_profile.html',
                  {'user_info': user_info,
                   'is_owner': is_owner,
                   'question_answer_pairs': question_answer_pairs,
                   'most_recent_review_info': most_recent_review_info},
                  content_type='text/html',
                  )


def profile_reviews(request, username):
    # Look up the user record who corresponds to this profile
    user = UserProfile.get_user_profile_from_username(username).user

    reviews = Review.objects.filter(reviewee=user.id)

    return render(request,
                  'user_profile/reviews.html',
                  {'reviews', reviews},
                  content_type='j',
                  )


def profile_tickets(request, username):
    # Look up the user record who corresponds to this profile
    user = UserProfile.get_user_profile_from_username(username).user

    tickets = Ticket.objects.filter(poster=user.id)

    return render(request,
                  'user_profile/tickets.html',
                  {'tickets', tickets},
                  content_type='text/html',
                  )
# Django core modules
from django.shortcuts import render
from django.db import transaction
from django.http.response import HttpResponseRedirect

# SpareStub modfules
from user_profile.forms import EditUserProfileForm, PasswordChangeForm
from user_profile.models import UserProfile, ProfileQuestion, ProfileAnswer
from reviews.models import Review
from tickets.models import Ticket

@transaction.atomic()
# We want updates to the user profile.html and user models to be atomic.
# I honestly cannot at the moment think of a scenario where updating one without the other would cause data integrity issues,
# but I am still wary of future changes to these models changing this fact.
def user_profile(request, username):
    if request.method == 'POST':
        edit_user_profile_form = EditUserProfileForm(request.POST)
        if edit_user_profile_form.is_valid():
            user = request.user
            user_profile = user.user_profile

            user.email = request.POST['email']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()

            user_profile.website = request.POST['website']
            user_profile.about = request.POST['about']
            user_profile.username = new_username = request.POST['username']

            user_profile.save()

            return HttpResponseRedirect('/profile.html/%s.html'.format(new_username))
    else:
        edit_user_profile_form = EditUserProfileForm() # An unbound form

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
    profile_answers = (ProfileAnswer.get_answer(question, user) for question in profile_questions)
    import pdb
    pdb.set_trace()
    profile_question_answer_pairs = zip(profile_questions.question, profile_answers.answer)

    return render(request,
                  'user_profile/profile.html',
                  {'user_info': user_info,
                   'is_owner': is_owner,
                   'profile_question_answer_pairs': profile_question_answer_pairs,
                   'most_recent_review_info': most_recent_review_info},
                  content_type='text/html',
                  )


def user_reviews(request, username):
    # Look up the user record who corresponds to this profile
    user = UserProfile.get_user_profile_from_username(username).user

    reviews = Review.objects.filter(reviewee=user.id)

    return render(request,
                  'user_profile/reviews.html',
                  {'reviews', reviews},
                  content_type='j',
                  )


def user_tickets(request, username):
    # Look up the user record who corresponds to this profile
    user = UserProfile.get_user_profile_from_username(username).user

    tickets = Ticket.objects.filter(poster=user.id)

    return render(request,
                  'user_profile/tickets.html',
                  {'tickets', tickets},
                  content_type='text/html',
                  )
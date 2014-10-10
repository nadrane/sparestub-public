# Django core modules
from django.shortcuts import render
from django.db import transaction
from django.http.response import HttpResponseRedirect

# Crowd Surfer moduels
from user_profile.forms import EditUserProfileForm, PasswordChangeForm


@transaction.atomic()
# We want updates to the user profile.html and user models to be atomic.
# I honestly cannot at the moment think of a scenario where updating one without the other would cause data integrity issues,
# but I am still wary of future changes to these models changing this fact.
def view_or_edit_profile(request, current_username):
    new_username = current_username # If a user changes their username, we actually redirect them to a different URL
                                    # than the URL they came from since the username is a piece of the URL
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
    return render(request,
                  'user_profile/profile.html',
                  {'edit_user_profile_form': edit_user_profile_form},
                  )
# Django imports
from django.contrib.auth.decorators import login_required
from .models import Ticket
from .forms

@login_required()
def submit_ticket(request):
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
                  {'form_s
# Django Imports
from django.shortcuts import render
from django.template.loader import render_to_string

# SpareStub Imports
from .forms import ContactForm
from .settings import contact_form_settings
from utils.miscellaneous import reverse_category_lookup, get_variable_from_settings
from utils.networking import ajax_popup_notification, ajax_http
from utils.email import send_email
from .settings import FEEDBACK_SUBMISSION_RESPONSE_SUBJECT, FEEDBACK_SUBMISSION_RESPONSE_TEMPLATE

SOCIAL_EMAIL_ADDRESS = get_variable_from_settings('SOCIAL_EMAIL_ADDRESS')


def submit(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject_type = contact_form.cleaned_data.get('subject_type')
            subject_type = reverse_category_lookup(subject_type, contact_form_settings.get('SUBJECT_TYPES'))
            body = contact_form.cleaned_data.get('body')
            from_email_address = contact_form.cleaned_data.get('from_email_address')

            # Send an email to shout@sparestub.com with the user's message
            send_email(SOCIAL_EMAIL_ADDRESS,
                       subject_type,
                       body,
                       from_email_address,
                       )

            # Also shoot the user who contacted us an email to let them know we'll get back to them soon.
            send_email(from_email_address,
                       FEEDBACK_SUBMISSION_RESPONSE_SUBJECT,
                       '',
                       SOCIAL_EMAIL_ADDRESS,
                       'SpareStub',
                       html=render_to_string(FEEDBACK_SUBMISSION_RESPONSE_TEMPLATE)
                       )

            # Notice that we always return True. If the email failed to send, we need to figure it out on our side.
            # There is nothing additional for the client to do.
            return ajax_popup_notification('success','We got your message! '
                                                     'Someone should respond to you within 24 hours.', 200)

        # If the user ignored out javascript validation and sent an invalid form, send back an error.
        # We don't actually specify what the form error was. This is okay because our app requires JS to be enabled.
        # If the user managed to send us an aysynch request with JS disabled, they aren't using the site as designed.
        # eg., possibly a malicious user. No need to repeat the form pretty validation already done on the front end.
        else:
            return ajax_http(False)
    else:
        contact_form = ContactForm()

    return render(request,
                  'contact/contact_form.html',
                  {'contact_form': contact_form,
                   'form_settings': contact_form_settings,
                   }
                  )
import json

from django.shortcuts import render, HttpResponse
from django.template.loader import render_to_string

from .forms import ContactForm
from .settings import contact_form_settings
from utils.miscellaneous import reverse_category_lookup, send_email

from .settings import social_email_address, auto_response_subject

def submit(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject_type = contact_form.cleaned_data.get('subject_type')
            subject_type = reverse_category_lookup(subject_type, contact_form_settings.get('SUBJECT_TYPES'))
            body = contact_form.cleaned_data.get('body')
            from_email_address = contact_form.cleaned_data.get('from_email_address')

            # Send an email to shout@sparestub.com with the user's message
            successful = send_email('shout@sparestub.com',
                                    subject_type,
                                    body,
                                    from_email_address,
                                    )

            auto_response_body = render_to_string('contact/contact_auto_response.html')
            # Also shoot the user who contacted us an email to let them know we'll get back to them soon.
            successful = send_email(from_email_address,
                                    auto_response_subject,
                                    '',
                                    social_email_address,
                                    'SpareStub',
                                    html=auto_response_body
                                    )

            # Notice that we always return True. If the email failed to send, we need to figure it out on our side.
            # THere is nothing additional for the client to do.
            return HttpResponse(json.dumps(True))

        # If the user ignored out javascript validation and sent an invalid form, send back an error.
        else:
            return HttpResponse(json.dumps(False))

    else:
        contact_form = ContactForm()

    return render(request,
                  'contact/contact_form.html',
                  {'contact_form': contact_form,
                   'form_settings': contact_form_settings,
                   }
                  )


def home(request):
    return render(request,
                  'home.html'
                  )
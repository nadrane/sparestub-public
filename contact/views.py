import json

from django.shortcuts import render, HttpResponse

from .forms import ContactForm
from .settings import contact_form_settings
from utils.miscellaneous import reverse_category_lookup, send_email


def submit(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject_type = contact_form.cleaned_data.get('subject_type')
            subject_type = reverse_category_lookup(subject_type, contact_form_settings.get('SUBJECT_TYPES'))
            body = contact_form.cleaned_data.get('body')
            from_email_address = contact_form.cleaned_data.get('from_email_address')

            successful = send_email('feedback@sparestub.com',
                                     subject_type,
                                     body,
                                     from_email_address
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
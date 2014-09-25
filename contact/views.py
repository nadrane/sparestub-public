# -*- coding: utf-8 -*-
import requests

import sendgrid

from django.shortcuts import render, redirect

from .forms import ContactForm
from .settings import contact_form_settings
from utils.miscellaneous import reverse_category_lookup


def submit(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject_type = contact_form.cleaned_data.get('subject_type', 'empty subject')
            subject_type = reverse_category_lookup(subject_type, contact_form_settings.get('SUBJECT_TYPES', ''))
            body = contact_form.cleaned_data.get('body', 'empty body')
            from_email_address = contact_form.cleaned_data.get('from_email_address', "nick@sparestub.com")
            sg = sendgrid.SendGridClient('SpareStub', 'rrY8qQVYwMsAV=Z^nTC4X')
            message = sendgrid.Mail()
            message.add_to('feedback@sparestub.com')
            message.set_subject(subject_type)
            message.set_html(body)
            message.set_from(from_email_address)
            status, msg = sg.send(message)

        #TODO it might be nice to just close to popup modal and submit the email using an ajax request later
        return redirect("contact.views.home")

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
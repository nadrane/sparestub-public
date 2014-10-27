# Django imports
from django.contrib.auth.decorators import login_required
from .settings import ticket_submit_form_settings
from django.shortcuts import render
from django.template.loader import render_to_string

#SpareStub imports
from .settings import email_submit_ticket_subject
from .models import Ticket
from .forms import SubmitTicketForm
from utils.networking import ajax_http

@login_required()
def submit_ticket(request):
    # If the form has been submitted by the user
    if request.method == 'POST':
        submit_ticket_form = SubmitTicketForm(request.POST)
        #Determine which form the user submitted.
        if submit_ticket_form.is_valid():
            title = submit_ticket_form.cleaned_data.get('title')
            price = submit_ticket_form.cleaned_data.get('price')
            location_raw = submit_ticket_form.cleaned_data.get('location_raw')
            location = submit_ticket_form.cleaned_data.get('location')
            start_datetime = submit_ticket_form.cleaned_data.get('start_datetime')
            ticket_type = submit_ticket_form.cleaned_data.get('type')
            payment_method = submit_ticket_form.cleaned_data.get('payment_method')
            about = submit_ticket_form.cleaned_data.get('about') or ''  # Might be empty

            Ticket.objects.create_ticket(poster=request.user,
                                         price=price,
                                         title=title,
                                         about=about,
                                         start_datetime=start_datetime,
                                         location_raw=location_raw,
                                         location=location,
                                         ticket_type=ticket_type,
                                         payment_method=payment_method,
                                         is_active=True,
                                         )

            email_submit_ticket_message = render_to_string('tickets/email_ticket_submit_message.html')

            # Also shoot the user who contacted us an email to let them know we'll get back to them soon.
            successful = request.user.send_mail(email_submit_ticket_subject,
                                                message='',
                                                html=email_submit_ticket_message
                                                )

            return ajax_http({'isSuccessful': True,
                              'notification_type': 'alert-success',
                              'notification_content': 'Your ticket was successfully submitted! It will become visible to others shortly.'
                              },
                             )

        # If the user ignored out javascript validation and sent an invalid form, send back an error.
        # We don't actually specify what the form error was. This is okay because our app requires JS to be enabled.
        # If the user managed to send us an aysynch request with JS disabled, they aren't using the site as designed.
        # eg., possibly a malicious user. No need to repeat the form pretty validation already done on the front end.
        else:
            return ajax_http(False, 400)

    return render(request,
                  'tickets/submit_ticket.html',
                  {'form_settings': ticket_submit_form_settings}
                  )


def search(request):

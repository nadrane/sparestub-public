# Django imports
from django.contrib.auth.decorators import login_required
from .settings import ticket_submit_form_settings
from django.shortcuts import render

#SpareStub imports
from .models import Ticket
from .forms import SubmitTicketForm
from utils.networking import ajax_http

@login_required()
def submit_ticket(request):
    # If the form has been submitted by the user
    if request.method == 'POST':
        if request.method == 'POST':
            submit_ticket_form = SubmitTicketForm(request.POST)
            #Determine which form the user submitted.
            if submit_ticket_form.is_valid():
                price = submit_ticket_form.cleaned_data.get('price')
                location_raw = submit_ticket_form.cleaned_data.get('location')
                location = submit_ticket_form.cleaned_data.get('database_location')
                start_datetime = submit_ticket_form.cleaned_data.get('start_datetime')
                ticket_type = submit_ticket_form.cleaned_data.get('type')
                payment_method = submit_ticket_form.cleaned_data.get('payment_method')
                about = submit_ticket_form.cleaned_data.get('about')  # Might be empty



                return ajax_http(True, 200, request=request)

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
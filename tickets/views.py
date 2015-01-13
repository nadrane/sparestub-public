# Django imports
from django.contrib.auth.decorators import login_required
from .settings import ticket_submit_form_settings
from django.shortcuts import render
from django.template.loader import render_to_string

# 3rd Party Imports
from haystack.views import FacetedSearchView

# SpareStub Imports
from utils.networking import ajax_http, form_success_notification, non_field_errors_notification

# Module Imports
from .models import Ticket
from .forms import SubmitTicketForm

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
            venue = submit_ticket_form.cleaned_data.get('venue')
            start_datetime = submit_ticket_form.cleaned_data.get('start_datetime')
            ticket_type = submit_ticket_form.cleaned_data.get('ticket_type')
            payment_method = submit_ticket_form.cleaned_data.get('payment_method', 'G')  # TODO Assume good faith since
                                                                                         # lean launch won't have secure
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
                                         status='P',
                                         venue=venue,
                                         )

            return ajax_http(**form_success_notification('Your ticket was successfully submitted! '
                                                         'It will become visible to others shortly.'))

        # If the user ignored out javascript validation and sent an invalid form, send back an error.
        # We don't actually specify what the form error was (unless it was a non_field error that we couldn't validate
        # on the front end). This is okay because our app requires JS to be enabled.
        # If the user managed to send us an aysynch request xwith JS disabled, they aren't using the site as designed.
        # eg., possibly a malicious user. No need to repeat the form pretty validation already done on the front end.
        else:
            return ajax_http(**non_field_errors_notification(submit_ticket_form))
    return render(request,
                  'tickets/submit_ticket.html',
                  {'form_settings': ticket_submit_form_settings}
                  )


class SearchResults(FacetedSearchView):
    template = 'search/search_results.html'
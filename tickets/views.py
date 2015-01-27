# Standard Imports
import logging
import stripe

# Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, redirect
from django.core.urlresolvers import reverse

# 3rd Party Imports
from haystack.views import FacetedSearchView

# SpareStub Imports
from utils.networking import ajax_http, ajax_popup_notification, non_field_errors_notification, ajax_other_message
from .settings import ticket_submit_form_settings
from stripe_data.models import create_customer_and_card, StripeError

# Module Imports
from .models import Ticket
from .forms import ValidTicketForm, SubmitTicketForm

@login_required()
def valid_ticket(request):
    """
    This function just checks if a ticket a user wishes to create has valid data.
    """
    if request.method == 'GET':
        valid_ticket_form = ValidTicketForm(request.GET)
        if valid_ticket_form.is_valid():
            return ajax_http(True, 200)
        return ajax_http(**non_field_errors_notification(valid_ticket_form))
    return ajax_http(False, 400)

@login_required()
def submit_ticket(request):
    # If the form has been submitted by the user
    if request.method == 'POST':
        submit_ticket_form = SubmitTicketForm(request.POST)
        #Determine which form the user submitted.
        if submit_ticket_form.is_valid():
            user = request.user
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
            token = submit_ticket_form.cleaned_data.get('token')
            card_id = submit_ticket_form.cleaned_data.get('card_id')


            try:
                customer, card = create_customer_and_card(user, token, card_id)
            except StripeError as e:
                logging.critical('Ticket creation failed')
                return ajax_other_message('Uh oh, it looks like our server broke! Our developers are on it.', 400)

            Ticket.objects.create_ticket(poster=request.user,
                                         price=price,
                                         title=title,
                                         about=about,
                                         start_datetime=start_datetime,
                                         location_raw=location_raw,
                                         location=location,
                                         ticket_type=ticket_type,
                                         payment_method=payment_method,
                                         card=card,
                                         status='P',
                                         venue=venue,
                                         )

            return ajax_popup_notification('success',
                                           'Your ticket was successfully submitted! '
                                           'It will become visible to others shortly.',
                                           200)

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


def can_delete_ticket(request, ticket_id):
    # Make sure that ticket exists
    try:
         ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return ajax_other_message("That ticket doesn't exist", 400)

    if not ticket.can_delete():
        return ajax_other_message("We're sorry. You cannot delete this ticket. Perhaps it has already been sold or "
                                  "cancelled. If you have any questions please contact us at Shout@sparestub.com.", 400)

    return ajax_http(True, 200)


def delete_ticket(request, ticket_id):
    """
    Delete the inputted ticket
    """

    user = request.user

    # Make sure that ticket exists
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404()

    # Make sure that the username entered is the actual poster of this ticket
    if ticket.poster != user:
        logging.critical('user id {} tried to delete ticket id {}, which is not his'.format(user.id, ticket.id))
        raise Http404()

    if ticket.can_delete():
        ticket.change_status('C')

        return redirect(reverse('profile_tickets', kwargs={'username': user.user_profile.username}))
    else:
        raise Http404()


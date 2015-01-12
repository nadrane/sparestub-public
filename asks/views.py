#Standard Imports
import logging

# Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# 3rd Party Imports
import stripe

#SpareStub Imports
from tickets.models import Ticket
from utils.networking import ajax_http, ajax_other_message
from stripe_data.models import Customer

# Module Imports
from .models import Request


@login_required()
def can_request_ticket(request, ticket_id):
    """
    Check to see if a user is a valid candidate to purchase a particular ticket.
    Check for 2 things:
        1. Make sure the user has not already requested to purchase this ticket.
        2. Make sure that the user has not requested to go to another show at the same time.
    """

    user = request.user
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except ObjectDoesNotExist:
        return ajax_other_message("Uh Oh, something went wrong. Our developers are on it!", 400)

    if not ticket.is_active:
        return ajax_other_message("It looks like the seller cancelled this ticket just a moment ago. Sorry!", 400)

    requests = Request.requests_for_ticket(user, ticket)
    # Allow the user to request to buy the ticket again only if the other requests were cancelled by
    # the requester or if the request expired
    if requests.exclude(status='E').exclude(status='C').exists():
        return ajax_other_message('You have already requested to buy this ticket. You cannot do that again!', 400)

    if Request.requested_other_ticket_same_time(user, ticket):
        return ajax_other_message("You cannot request this ticket because you've already"
                                  " requested a ticket within two hours of this event", 400)

    return ajax_http(True)


@login_required()
def request_to_buy(request):
    user = request.user

    try:
        ticket = Ticket.objects.filter(pk=request.POST.get('ticket_id'))[0]
    except Ticket.DoesNotExist:
        raise Http404()

    if ticket.poster == user:
        logging.warning('User cannot request to buy their own ticket')
        raise Http404()

    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here https://dashboard.stripe.com/account
    stripe.api_key = settings.STRIPE_SECRET_API_KEY

    # Get the token that stripe sent us
    token = request.POST.get('token[id]')

    # Create a customer record to store the credit card information in the Stripe system.
    # We can use this information to charge the customer later.
    try:
        # Check to see if a customer record exists for this user. If it already does, we only need to create
        # a request record.
        if not Customer.customer_exists(user):
            customer = stripe.Customer.create(card=token)
            Customer.objects.create_customer(stripe_id=customer.id, user=user)
        Request.objects.create_request(ticket, user)
    except stripe.CardError as e:
        logging.critical('Stripe failed with error {}'.format(e))

    return ajax_http(True)
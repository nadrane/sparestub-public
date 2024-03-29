#Standard Imports
import logging

# Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import Http404
from django.core.exceptions import ObjectDoesNotExist

# 3rd Party Imports
import stripe

#SpareStub Imports
from tickets.models import Ticket
from utils.networking import ajax_http, ajax_other_message, ajax_popup_notification
from stripe_data.models import StripeError, create_customer_and_card, Customer
from registration.models import User

# Module Imports
from .models import Request

@login_required()
def accept_request(request):
    user = request.user    # This is the owner of the ticket
    try:
        ticket = Ticket.objects.get(pk=request.POST.get('ticket_id'))
    except Ticket.DoesNotExist:
        return ajax_popup_notification('danger', 'Uh Oh, something went wrong. Our developers are on it!', 400)

    if ticket.poster != user:
        logging.critical('Fraudulent request detected {} tried to accept a ticket posted by {}'
                         .format(user, ticket.poster))
        return ajax_popup_notification('danger', 'Uh Oh, something went wrong. Our developers are on it!', 400)

    try:
        other_user = User.objects.get(pk=request.POST.get('other_user_id'))
    except User.DoesNotExist:
        return ajax_popup_notification('danger', 'Uh Oh, something went wrong. Our developers are on it!', 400)

    user_request = Request.get_last_request(other_user, ticket)

    if user_request.status == 'A':
        return ajax_popup_notification('success', "You've already accepted this ticket!", 400)

    if user_request.status != 'P':
        return ajax_popup_notification('danger', 'There is no outstanding request for this ticket.', 400)

    if not ticket.is_requestable():
        return ajax_popup_notification('warning', 'It looks like this ticket is no longer available', 400)

    customer1 = Customer.get_customer_from_user(other_user)
    customer2 = Customer.get_customer_from_user(user)
    if not (customer1 and customer2):
        if not customer1:
            logging.critical('Failed to accept request {}. '
                             'Customer information not available for user {}'
                             .format(user_request.id), other_user)
        if not customer2:
            logging.critical('Failed to accept request {}. '
                             'Customer information not available for user {}'
                             .format(user_request.id), user)
        return ajax_popup_notification('danger', 'Uh Oh, something went wrong. Our developers are on it!', 400)

    # Charge them first. We actually might have a scenario where one of the cards is declined
    try:
        customer1.charge(500, user_request.card)
        customer2.charge(500, ticket.card)
    except StripeError as e:
        return ajax_popup_notification('danger', "One of the payments didn't quite go through. We'll follow up with you")

    user_request.accept()
    return ajax_popup_notification('success', "Congratulations, you accepted {}'s request"
                                   .format(other_user.first_name.title()), 200)

@login_required()
def decline_request(request):
    user = request.user
    try:
        ticket = Ticket.objects.get(pk=request.POST.get('ticket_id'))
    except Ticket.DoesNotExist:
        return ajax_popup_notification('danger', 'Uh Oh, something went wrong. Our developers are on it!', 400)

    if ticket.poster != user:
        logging.critical('Fraudulent request detected {} tried to decline a ticket posted by {}'
                         .format(user, ticket.poster))
        return ajax_popup_notification('danger', 'Uh Oh, something went wrong. Our developers are on it!', 400)

    if not ticket.is_requestable:
        return ajax_popup_notification('warning', 'It looks like this ticket is no longer available', 400)

    try:
        other_user = User.objects.get(pk=request.POST.get('other_user_id'))
    except User.DoesNotExist:
        return ajax_popup_notification('danger', 'Uh Oh, something went wrong. Our developers are on it!', 400)

    user_request = Request.get_last_request(other_user, ticket)

    if user_request.status == 'D':
        return ajax_popup_notification('success', "You've already declined this ticket!", 400)

    if user_request.status != 'P':
        return ajax_popup_notification('info', 'There is no outstanding request for this ticket.', 400)

    user_request.decline()

    return ajax_popup_notification('info', "Aww, we'll let {} down easy. Good luck finding another gig buddy."
                                   .format(other_user.first_name.title()), 200)

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

    if not ticket.is_requestable():
        return ajax_other_message("It looks like this ticket is no longer available. Sorry!", 400)

    if not Request.can_request(ticket, user):
        return ajax_other_message('You have already requested to buy this ticket. You cannot do that again!', 400)

    if Request.requested_other_ticket_same_time(user, ticket):
        return ajax_other_message("You cannot request this ticket because you've already"
                                  " requested a ticket within two hours of this event", 400)

    return ajax_other_message('Your request has been submitted', 200)


@login_required()
def request_to_buy(request):
    user = request.user
    try:
        ticket = Ticket.objects.get(pk=request.POST.get('ticket_id'))
    except Ticket.DoesNotExist:
        raise Http404()

    # Do this validation again...
    if not Request.can_request(ticket, user) or Request.requested_other_ticket_same_time(user, ticket):
        return ajax_http(False, 400)

    if ticket.poster == user:
        logging.warning('User cannot request to buy their own ticket')
        return ajax_http(False, 400)

    # Get the token and card that stripe sent us
    token = request.POST.get('token')
    card_id = request.POST.get('card_id')

    if not token or not card_id:
        logging.info('Request to buy submitted without Stripe token for {}'.format(user))
        return ajax_other_message('Your request was unable to be processed. Our developers are on it!', 400)

    try:
        customer, card = create_customer_and_card(user, token, card_id)
    except StripeError as e:
        logging.critical('Request creation failed')
        return ajax_other_message('Your request was unable to be processed. Our developers are on it', 400)

    Request.objects.create_request(ticket, user, card)

    return ajax_other_message('Your request to buy has been submitted. '
                              'Your card will be charged if the seller accepts your request.', 200)

@login_required()
def cancel_request_to_buy(request):
    """
    Mark a pending request as cancelled
    """
    user = request.user

    # Make sure that ticket exists
    try:
        ticket = Ticket.objects.get(pk=request.POST.get('ticket_id'))
    except Ticket.DoesNotExist:
        ajax_other_message('Uh oh, something went wrong', 400)

    # Make sure that the username entered is the actual poster of this ticket
    request = Request.objects.filter(requester=user, ticket=ticket, status='P')
    if request:
        request[0].cancel()
        return ajax_other_message('Your request has been cancelled', 200)
    else:
        return ajax_other_message('You do not have a pending request', 400)



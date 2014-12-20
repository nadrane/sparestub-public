#Standard Imports
import logging

# Django imports
from django.contrib.auth.decorators import login_required
from .settings import ticket_submit_form_settings
from django.shortcuts import render, Http404, HttpResponseRedirect
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist

# 3rd Party Imports
from haystack.views import FacetedSearchView
import stripe

#SpareStub Imports
from .settings import email_submit_ticket_subject, search_results_settings
from .models import Ticket, Bid
from .forms import SubmitTicketForm
from utils.networking import ajax_http, form_success_notification, form_failure_notification, \
    non_field_errors_notification
from django.conf import settings

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
                                         is_active=True,
                                         venue=venue,
                                         )

            email_submit_ticket_message = render_to_string('tickets/email_ticket_submit_message.html')

            # Also shoot the user who contacted us an email to let them know we'll get back to them soon.
            request.user.send_mail(email_submit_ticket_subject,
                                   message='',
                                   html=email_submit_ticket_message
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


@login_required()
def request_to_buy(request, ticket_id):
    user = request.user

    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return Http404()

    if ticket.poster == user:
        logging.warning('User cannot request to buy their own ticket')
        return Http404()


    # Set your secret key: remember to change this to your live secret key in production
    # See your keys here https://dashboard.stripe.com/account
    stripe.api_key = settings.STRIPE_SECRET_API_KEY

    charge_amount = ticket.convert_price_to_stripe_amount()

    # Get the credit card details submitted by the form
    token = request.POST['stripeToken']

    # Create the charge on Stripe's servers - this will charge the user's card
    try:
        charge = stripe.Charge.create(amount=charge_amount,  # amount in cents, again
                                      currency="usd",
                                      card=token,
                                      description='charge for ticket {}'.format(ticket.id)
                                      )

        bid = Bid.objects.create_bid(ticket, user)

    except stripe.CardError as e:

        # If the user looking at this profile is its owner, then we want to render a couple edit buttons
        if request.user == user:
            is_owner = True
        else:
            is_owner = False

        username = user.user_profile.username

        user_location = user.location

        most_recent_review = user.most_recent_review()

        user_info = {'name': user,
                     'age': user.age(),
                     'city': user_location.city,
                     'state': user_location.state,
                     'rating': user.rating,
                     'username': username,
                     }

        try:
            user_info['profile_picture'] = user.profile_picture
        except ObjectDoesNotExist:
            pass

        if most_recent_review:
            reviewer_location = most_recent_review.reviewer.location
            reviewer_city, reviewer_state = reviewer_location.city, reviewer_location.state
            most_recent_review_info = {'name': most_recent_review.reviewer.get_short_name(),
                                       'age': most_recent_review.reviewer.age(),
                                       'city': reviewer_city,
                                       'state': reviewer_state,
                                       'contents': most_recent_review.contents,
                                       'rating': most_recent_review.rating
                                       }
        else:
            most_recent_review_info = None

        # The card has been declined
        return render(request,
                      'user_profile/view_ticket.html',
                      {'user_info': user_info,
                       'is_owner': is_owner,
                       'ticket': ticket,
                       'most_recent_review_info': most_recent_review_info,
                       'stripe_public_api_key': settings.STRIPE_PUBLIC_API_KEY,
                       'card_declined': True
                       },
                      content_type='text/html',
                      )

    return HttpResponseRedirect('/')
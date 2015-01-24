# Standard Imports
from itertools import chain
from django.utils import timezone as django_timezone # Need to rename to avoid conflicting with pytz
import logging

# 3rd Party Imports
from pytz import timezone

# Django
from utils.models import TimeStampedModel
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.db import transaction
from django.template.loader import render_to_string

# SparStub imports
from registration.models import User
from .settings import ticket_model_settings, POST_TICKET_SUBMIT_SUBJECT, POST_TICKET_SUBMIT_TEMPLATE
from asks.settings import REQUEST_INACTIVE_SUBJECT, REQUEST_INACTIVE_TEMPLATE
from locations.models import Location


class TicketManager(models.Manager):

    def create_ticket(self, poster, price, title, start_datetime, location_raw, location, ticket_type, payment_method,
                      venue, status='P', about=None):
        """
        Creates a ticket record using the given input
        """
        ticket_timezone = timezone(location.timezone)
        start_date = ticket_timezone.normalize(start_datetime.astimezone(ticket_timezone)).date()

        rating = poster.rating

        ticket = self.model(poster=poster,
                            bidders=None,  # Bidders cannot exist at ticket creation
                            price=price,
                            title=title,
                            about=about,
                            start_datetime=start_datetime,
                            start_date=start_date,
                            location_raw=location_raw,
                            location=location,
                            venue=venue,
                            ticket_type=ticket_type,
                            payment_method=payment_method,
                            status=status,
                            rating=rating,
                            )

        ticket.save()

        logging.info('Ticket created {}'.format(repr(ticket)))

        # Also shoot the user who contacted us an email to let them know we'll get back to them soon.
        message_body = render_to_string(POST_TICKET_SUBMIT_TEMPLATE,
                                {'user': poster})
        poster.send_mail(POST_TICKET_SUBMIT_SUBJECT,
                         message='',
                         html=message_body
                         )

        return ticket


class Ticket(TimeStampedModel):
    poster = models.ForeignKey(User,
                               blank=False,
                               null=False,
                               db_index=True,
                               related_name='poster',
                               )

    bidders = models.ForeignKey(User,
                                blank=True,
                                null=True,
                                db_index=True,
                                related_name='bidders',
                                )

    price = models.FloatField(blank=False)

    title = models.CharField(blank=False,
                             max_length=ticket_model_settings.get('TITLE_MAX_LENGTH'),
                             )

    about = models.TextField(blank=True,
                             default='',
                             max_length=ticket_model_settings.get('ABOUT_MAX_LENGTH'))

    # When does the event start? Stored in UTC timezone format
    start_datetime = models.DateTimeField(blank=False)

    # This date is used for search ticket queries exclusively.
    # This is the date of the event in the timezone of the event.
    # When start_datetime is submitted, we convert the datetime to UTC, possibly changing the date of the event.
    # When we query a date range against the start_date of an event, we want that date to be in the timezone of
    # the event's location. Haystack isn't going to convert all of the start_datetimes back to the timezone of the
    # event's location for us, so let's just keep a copy of that date here. Redundant, but we'll live.
    start_date = models.DateField(blank=False)

    # The city and state that the user originally entered in the form.
    location_raw = models.CharField(blank=False,
                                    max_length=254)  # Keep the city, state combo around just in case we are
                                                     # we need to debug

    # The system tries to map the raw input form the user to a location record. That's what this is.
    location = models.ForeignKey(Location,    # We are going to map the inputted city, state to a zipcode
                                 blank=False
                                 )

    venue = models.CharField(max_length=ticket_model_settings.get('VENUE_MAX_LENGTH'),
                             blank=False,
                             null=False,
                             )

    ticket_type = models.CharField(blank=False,
                                   max_length=1,
                                   choices=ticket_model_settings.get('TICKET_TYPES'))

    payment_method = models.CharField(blank=False,
                                      max_length=1,
                                      choices=ticket_model_settings.get('PAYMENT_METHODS'))

    # An active ticket is one that is available to be bid on
    status = models.CharField(blank=False,
                              db_index=True,
                              default='P',
                              max_length=1,
                              choices=ticket_model_settings.get('TICKET_STATUSES'),
                              )

    # The rating of the user that posted the ticket. Do not use this field!! Reference the poster rating instead.
    # Yes, they should always be the same, but let's just be safe. This field exists solely because Haystack cannot
    # let us index tickets on a field of the poster even though that's exactly what we need to do.
    rating = models.IntegerField(blank=True,
                                 null=True,
                                 default=None,
                                 )

    objects = TicketManager()

    def __repr__(self):
        return '{class_object} - {id} \n'\
               'Poster: {poster}'\
               .format(class_object=self.__class__,
                       id=self.id,
                       poster=repr(self.poster))

    def __str__(self):
        return self.title

    def can_delete(self):
        """
        Return whether a ticket can be deleted or not
        """

        if self.get_buyer():
            return False
        return True

    def get_buyer(self):
        """
        Return the buyer of a ticket by looking at it's associated requests
        """

        from asks.models import Request
        requests = Request.objects.filter(ticket=self, status='A')
        if requests:
            return requests[0]
        return None

    @staticmethod
    def completed_but_not_expired():
        """
        Return a QuerySet of tickets whose event date and time has passed but has not been marked as expired.
        """
        return Ticket.objects.filter(Q(status='P') | Q(status='S')).filter(start_datetime__lte=django_timezone.now())


    def is_messageable(self):
        """
        A user is allowed to message another user about a particular ticket if it has a status of posted, sold, or expired.
        Obviously not any user can send the message, but some user's can. For example, the user that bought the ticket
        can send a message if the ticket has a status of sold.
        """
        status = self.status
        return status == 'P' or status == 'S' or status == 'E'

    def is_requestable(self):
        """
        Is this ticket available for requests. A ticket may only be requested if it's status is posted
        """
        return self.status == 'P'

    def can_view(self, user):
        """
        Is this ticket viewable? A ticket is not viewable if
        """
        is_viewable = None
        status = self.status
        poster = self.poster

        # If the ticket is posted, anyone may view it
        if status == 'P':
            is_viewable = True
        # If the user cancelled the ticket, only he may view it
        elif status == 'C':
            if poster == user:
                is_viewable = True
            else:
                is_viewable = False
        # If the buyer's account was deactivated, no one may see the request
        elif status == 'D':
            is_viewable = False
        # If the ticket is sold or the event has passed, only the buyer and seller may see it
        elif status == 'E' or status == 'S':
            if poster == user or poster == self.get_buyer():
                is_viewable = True
            else:
                is_viewable = False

        return is_viewable

    @transaction.atomic()
    def change_status(self, new_status):
        from asks.models import Request
        from messages.models import Message

        # Ticket posted by seller
        if new_status == 'P':
            pass

        # Ticket cancelled by seller
        elif new_status == 'C':
            # Mark all of the associated requests as cancelled
            # We only care about requests that are pended and expired. These are the only user's who care to learn more.
            requests = Request.objects.filter(ticket=self).filter(Q(status='P') | Q(status='E'))\
                                      .order_by('requester').distinct('requester')   # Handle users that had an expired request that re-requested
            requests.update(status='T')
            users_messaged = set()  # Maintain a set of users who have already been messaged
            potential_users_to_message = set()  # A second set of users who might need to be messaged if they aren't in the first set
            for request in requests:
                users_messaged.add(request.requster)
                request.ticket_cancelled()

            # Then add in conversations where there was no request sent.
            # These people clearly had an interest in the ticket.
            # We don't want to just block their conversations abruptly.
            messages = Message.objects.filter(ticket=self)
            poster = self.poster
            for message in messages:
                sender = message.sender
                if sender != poster:
                    potential_users_to_message.add(sender)
                else:
                    potential_users_to_message.add(message.receiver)
            message_body = 'This is an automated message to let you know that {} ' \
                           'has cancelled this ticket.'.format(poster.first_name.title())

            # Remove the users we have already messaged
            for user in potential_users_to_message.difference(users_messaged):

                # Continue to remove users we've already messaged based on if they have a requesy
                user_requests = Request.objects.filter(requester=user)

                # If there is no request or the request is expired, we want to send them a message
                # Unlike pending requests, these requests remain expired
                if not user_requests.exists():
                    Message.objects.create_message(poster, user, self, message_body, False)

        # Event date has passed and ticket expired
        elif new_status == 'E':
            # Update all expired requests to a status of closed.
            self.get_requests().filter(status='E').update(status='C')

            # Update the ticket status last in case the task that calls this crashes. That way any expired requests
            # that didn't get marked as closed will be caught the next time the task runs
            self.status = 'E'
            self.save()

        # Ticket sold... seller accepted request to buy
        # Should only be called by requests.models.Request.accept, so there won't be additional handling for the
        # attached request. But there will be for other requests for that ticket.
        elif new_status == 'S':
            # Change all other requests besides the calling request to Ticket Sold.
            # The other request is changed to accepted in self.accept
            # That means that a different user purchased the ticket.
            requests = self.get_requests().filter(status='P')
            requests.update(status='S')
            for request in requests:
                request.requster.send_mail(REQUEST_INACTIVE_SUBJECT,
                                           message='',
                                           html=render_to_string(REQUEST_INACTIVE_TEMPLATE))

        # User account deactivated, and ticket deactivated along with it
        elif new_status == 'D':
            pass # TODO figure out how to handle this
            #for request in requests:
            #    request.requster.send_mail()

        old_status = self.status
        self.status = new_status
        self.save()
        logging.info('Ticket status change from {old_status} to {new_status}\n'
                     '{ticket}'.format(old_status=old_status,
                                       new_status=new_status,
                                       ticket=self)
                     )

    def convert_price_to_stripe_amount(self):
        """
        Takes a ticket price as input and converts it to cents, removing the decimal in the process.
        This is necessary because Stripe only accepts charges that are formatted in cents
        """
        price_in_cents = int(float(self.price) * 100)

        # Add the 5 dollar base transaction fee
        price_in_cents += 500

        if self.payment_method == 'S':
            price_in_cents *= 1.05

        return round(price_in_cents)

    def get_absolute_url(self):
        return reverse('view_ticket', kwargs={'username': self.poster.user_profile.username,
                                              'ticket_id': self.id,
                                              })

    def get_full_location(self):
        return self.location.city.title() + ', ' + self.location.state.upper() + '-' + self.venue.title()

    def get_formatted_start_datetime(self):
        """
        Get the start date and time in the timezone of the ticket's location. The start_datetime field is in UTC.
        """

        ticket_timezone = timezone(self.location.timezone)
        return ticket_timezone.normalize(self.start_datetime.astimezone(ticket_timezone))

    def get_requests(self):
        """
        Returns a QuerySet containing all Request records associated with the calling ticket.
        """
        from asks.models import Request
        return Request.objects.filter(ticket=self)

    @staticmethod
    def available_tickets(user):
        """
        Return a QuerySet of tickets that this user posted that are still available to buy
        """
        return Ticket.objects.filter(poster=user, status='P').order_by('start_datetime')

    @staticmethod
    def in_progress_ticket(user):
        """
        Return a QuerySet of tickets that are in progress for this user.
        This list is aggregated from both active conversations and from active requests.
        Any ticket with an associated request of
            1. Accepted
            2. Pending
        will be added to this list if that ticket has a status of
            1. Sold
            2. Posted
        """
        from messages.models import Message
        from asks.models import Request

        # Get any open accepted and pending requests for sold and posted tickets
        open_requests = Request.objects.filter(Q(status='A') | Q(status='P'))\
                                       .filter(Q(ticket__status='S') | Q(ticket__status='P'))

        # Get the tickets that this user has messaged other users about.
        # We do not care about messages I've received because those ticket's
        # are available in the "available tickets" section
        # We only care about posted tickets, not sold ones. If a sold one was relevant to me,
        # it would be bundled up from the Request
        active_messages = Message.get_messages_sent(user).exclude(ticket__poster=user).filter(ticket__status='P')

        # Filter out duplicate tickets. There are lots of messages between two people about one ticket,
        # and potentially multiple requests for that matter
        tickets_requested = set(request.ticket for request in open_requests)
        tickets_messaged_about = set(message.ticket for message in active_messages)

        return tickets_requested.union(tickets_messaged_about)

    @staticmethod
    def past_tickets(user):
        """
        Returns a QuerySet of tickets that this user either successfully bought or successfully sold
        """
        from asks.models import Request

        tickets_sold_and_cancelled_tickets = Ticket.objects.filter(poster=user).filter(Q(status='S') | Q(status='C'))
        requests_for_tickets = Request.objects.filter(requester=user, ticket__status='S')

        # An if statement on the return from chain actually passes... so return None explicitly if there's nothing
        if not tickets_sold_and_cancelled_tickets and not requests_for_tickets:
            return None

        return set(chain(tickets_sold_and_cancelled_tickets, [request.ticket for request in requests_for_tickets]))

    @staticmethod
    def upcoming_tickets(user):
        """
        Returns a QuerySet of tickets that this user either successfully bought or successfully sold
        """
        from asks.models import Request

        upcoming_shows_user_posted = Ticket.objects.filter(poster=user, status='S')
        upcoming_shows_user_requested = Request.objects.filter(requester=user, status='A')

        # An if statement on the return from chain actually passes... so return None explicitly if there's nothing
        if not upcoming_shows_user_posted and not upcoming_shows_user_requested:
            return None

        return set(chain(upcoming_shows_user_posted, [request.ticket for request in upcoming_shows_user_requested]))

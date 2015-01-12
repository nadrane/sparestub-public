# 3rd Party Imports
from pytz import timezone

# Django
from utils.models import TimeStampedModel
from django.db import models
from django.core.urlresolvers import reverse

# SparStub imports
from registration.models import User
from .settings import ticket_model_settings
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
                             max_length=ticket_model_settings.get('CONTENT_MAX_LENGTH'))

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
    status = models.BooleanField(blank=False,
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

    def __str__(self):
        return self.title

    def change_status(self, new_status):
        from asks.models import Request

        # Ticket posted by seller
        if new_status == 'P':
            pass
        # Ticket cancelled by seller
        elif new_status == 'C':
            # Mark all of the associated requests as cancelled
            requests = Request.objects.filter(ticket=self)
            requests.update(status='T')
            for request in requests:
                request.cancel()
        # Event date has passed and ticket expired
        elif new_status == 'E':
            pass
        # Ticket sold... seller accepted request to buy
        # Should only be called by requests.models.Request.accept, so there won't be additional handling for the
        # attached request. But there will be for other requests for that ticket.
        elif new_status == 'S':
            # Change all other requests besides the calling request to Ticket Sold.
            # That means that a different user purchased the ticket.
            requests = self.get_requests().filter(status='P').update('S')
            for request in requests:
                request.requster.send_mail()
        # User account deactivated, and ticket deactivated along with it
        elif new_status == 'D':
            pass

        self.status = new_status
        self.save()

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
        from requests.models import Request
        return Request.objects.filter(ticket=self)

    @staticmethod
    def available_tickets(user):
        """
        Return a QuerySet of tickets that this user posted that are still active
        """
        return Ticket.objects.filter(poster=user, is_active=True)

    @staticmethod
    def in_progress_ticket(user):
        """
        Return a QuerySet of tickets that this user not not post that he has has either messaged another user about or
        that he has requested to buy.
        """
        from messages.models import Message

        # Get the tickets that this user has messaged other users about
        active_messages = Message.get_messages_received(user).filter(is_active=True)

        # Filter out duplicate tickets. There are lots of messages between two people about one ticket.
        tickets_messaged_about = set(message.ticket for message in active_messages)

        # Get the tickets that this user has bid on that are still pending
        # TODO include bids once they exist
        #tickets_requested = Bid.objects.filter(bidder=user).filter(status='P').ticket
        #return chain(tickets_messaged_about, tickets_requested)

        return tickets_messaged_about

    @staticmethod
    def past_tickets(user):
        """
        Returns a QuerySet of tickets that this user either successfully bought or successfully sold
        """
        return Ticket.objects.filter(Q(poster=user) | Q(bidders=user)).filter(is_active=False)
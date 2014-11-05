# 3rd Party Imports
from pytz import timezone

# Django
from utils.models import TimeStampedModel
from django.db import models

# SparStub imports
from registration.models import User
from .settings import ticket_model_settings
from locations.models import Location


class TicketManager(models.Manager):

    def create_ticket(self, poster, price, title, start_datetime, location_raw, location, ticket_type, payment_method,
                      is_active, about=None):
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
                            ticket_type=ticket_type,
                            payment_method=payment_method,
                            is_active=is_active,
                            rating=rating,
                            )

        ticket.save(using=self._db)

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

    ticket_type = models.CharField(blank=False,
                                   max_length=1,
                                   choices=ticket_model_settings.get('TICKET_TYPES'))

    payment_method = models.CharField(blank=False,
                                      max_length=1,
                                      choices=ticket_model_settings.get('PAYMENT_METHODS'))

    is_active = models.BooleanField(blank=False,
                                    default=False)

    deactivation_reason = models.CharField(blank=True,
                                           max_length=1,
                                           default='',
                                           choices=ticket_model_settings.get('DEACTIVATION_REASONS'))

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

    def get_absolute_url(self):
        return "/tickets/%id/" % self.id

    # TODO use reverse url once views are defined
    #from django.core.urlresolvers import reverse
    #return reverse('people.views.details', args=[str(self.id)])

    def get_formatted_start_datetime(self):
        """
        Get the start date and time in the timezone of the ticket's location. The start_datetime field is in UTC.
        """

        ticket_timezone = timezone(self.location.timezone)
        return ticket_timezone.normalize(self.start_datetime.astimezone(ticket_timezone))


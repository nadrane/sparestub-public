#Django
from utils.models import TimeStampedModel
from django.db import models

#SparStub imports
from registration.models import User
from .settings import ticket_model_settings
from locations.models import Location


class TicketManager(models.Manager):

    def create_ticket(self, poster, price, title, start_datetime, location_raw, location, ticket_type, payment_method,
                      is_active, about=None):
        '''
            Creates a ticket record using the given input
        '''

        ticket = self.model(poster=poster,
                            bidders=None,  # Bidders cannot exist at ticket creation
                            price=price,
                            title=title,
                            about=about,
                            start_datetime=start_datetime,
                            location_raw=location_raw,
                            location=location,
                            ticket_type=ticket_type,
                            payment_method=payment_method,
                            is_active=is_active,
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

    # When does the event start?
    start_datetime = models.DateTimeField(blank=False)

    # The city and state that the user originally entered in the form.
    location_raw = models.CharField(blank=False,
                                    max_length=254)  # Keep the city, state combo around just in case we are
                                                     # we need to debug

    # The system tries to map the raw input form the user to a location record. That's what this is.
    location = models.ForeignKey(Location, # We are going to map the inputted city, state to a zipcode
                                 blank=False
                                 )

    ticket_type = models.CharField(blank=False,
                            max_length=1,
                            choices=ticket_model_settings.get('TICKET_TYPES'))

    payment_method = models.CharField(blank=False,
                                      max_length=1,
                                      choices=ticket_model_settings.get('PAYMENT_METHODS'))

    is_active = models.BooleanField(blank=False)

    objects = TicketManager()



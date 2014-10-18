# Standard Python modules
import os

#Django
from utils.models import TimeStampedModel
from django.db import models

#SparStub imports
from registration.models import User
from .settings import review_model_settings


class Ticket(TimeStampedModel):
    poster = models.ForeignKey(User,
                               blank=False,
                               null=False,
                               db_index=True,
                               )

    bidders = models.ManyToManyField(User,
                                     blank=True,
                                     null=True,
                                     db_index=True,
                                     )

    price = models.IntegerField(blank=False)

    title = models.CharField(blank=False,
                             max_length=100,
                             )

    contents = models.TextField(max_length=review_model_settings.get('CONTENT_MAX_LENGTH'))


    event_location_raw = models.CharField(max_length=254)  # Keep the city, state combo around just in case we are
                                                           # we need to debug
    event_location = models.IntegerField(max_length=5)  # We are going to map the inputted city, state to a zipcode

    artist = models.ForeignKey
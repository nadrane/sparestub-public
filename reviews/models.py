# Standard Python modules
import os

#Django
from utils.models import TimeStampedModel
from django.db import models

#SparStub imports
from registration.models import User
from .settings import review_model_settings


class Review(TimeStampedModel):
    reviewer = models.ForeignKey(User,
                                 blank=False,
                                 null=False,
                                 db_index=True,
                                 related_name='reviewer',
                                 )

    reviewee = models.ForeignKey(User,
                                 blank=False,
                                 null=False,
                                 db_index=True,
                                 related_name='reviewee',
                                 )

    rating = models.IntegerField(max_length=5)

    contents = models.TextField(max_length=review_model_settings.get('CONTENT_MAX_LENGTH'))
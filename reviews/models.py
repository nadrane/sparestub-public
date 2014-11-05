# Standard Python modules
import os

#Django
from utils.models import TimeStampedModel
from django.db import models, transaction

#SparStub imports
from registration.models import User
from tickets.models import Ticket
from .settings import review_model_settings


class ReviewManager(models.Manager):
    # Whenever we create a review, we update the aggregate rating on the user record.
    # We also update the ticket ratings of that user.
    # Make sure we do not do one without doing the other by making the function atomic.
    @transaction.atomic()
    def create_review(self, reviewer, reviewee, contents, rating):
        """
            Creates a review record using the given input
        """

        review = self.model(reviewer=reviewer,
                            reviewee=reviewee,
                            contents=contents,
                            rating=rating,
                            )

        review.save(using=self._db)

        # Needs to do after the submitted review so that it is included in the calculation.
        # TODO - Does it matter that this whole thing is atomic? Will that cause calculate rating to miss this review?
        new_rating, reviewee.rating = reviewee.calculate_rating()
        reviewee.save(using=self._db)

        # The ticket also contains the rating of it's poster. Make sure to update all active tickets for this user.
        for ticket in Ticket.objects.filter(poster=reviewee.id):
            ticket.rating = new_rating
            ticket.save(using=self._db)

        return review


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

    objects = ReviewManager()
__author__ = 'nicholasdrane'
import logging
from datetime import date

from django.core.management.base import BaseCommand

from .empty_db import recreate_empty_database
from registration.models import User
from reviews.models import Review


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        recreate_empty_database()
        self.create_users()


    def create_users(self):
        logging.debug('Creating user and person objects')
        # Create my user
        User.objects.create_superuser('nick@gmail.com',
                                      'password',
                                      'nick',
                                      'drane',
                                      zipcode='11102',
                                      birth_date=date(1989,1,28)
                                      )

        User.objects.create_superuser('andy@gmail.com',
                                      'password',
                                      'andy',
                                      'drane',
                                      zipcode='02445',
                                      birth_date=date(1989,1,28)
                                      )

        User.objects.create_superuser('stephanie@gmail.com',
                                      'password',
                                      'stephanie',
                                      'macconnell',
                                      zipcode='11103',
                                      birth_date=date(1989,1,28)
                                      )

        User.objects.create_superuser('chris@gmail.com',
                                      'password',
                                      'chris',
                                      'drane',
                                      zipcode='11215',
                                      birth_date=date(1989,1,28)
                                      )
        return

    def create_reviews(self):
        reviewer = User.objects.all()[1]
        reviewee = User.objects.all()[2]
        rating = 4
        x = Review(reviewer, reviewee, rating, 'terrible')
        x.save()



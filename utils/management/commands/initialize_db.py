__author__ = 'nicholasdrane'
import logging
from datetime import date

from django.core.management.base import BaseCommand

from .empty_db import recreate_empty_database
from registration.models import User
from reviews.models import Review
from locations.models import Location
from django.core.management import call_command
from locations.management.commands import process_zip_codes

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        import pdb
        pdb.set_trace()
        # Recreate the tables in the database according to our models
        recreate_empty_database()
        self.create_users()
        self.create_reviews()

    @staticmethod
    def create_users():
        logging.debug('Creating user and person objects')
        # Create my user
        User.objects.create_superuser('nick@sparestub.com',
                                      'password',
                                      'nick',
                                      'drane',
                                      location=Location.objects.filter(zip_code='11102')[0],
                                      birth_date=date(1989,1,28)
                                      )

        User.objects.create_superuser('andy@gmail.com',
                                      'password',
                                      'andy',
                                      'drane',
                                      location=Location.objects.filter(zip_code='11103')[0],
                                      birth_date=date(1989,1,28)
                                      )

        User.objects.create_superuser('stephanie@sparestubbase.com',
                                      'password',
                                      'stephanie',
                                      'macconnell',
                                      location=Location.objects.filter(zip_code='11103')[0],
                                      birth_date=date(1989,1,28)
                                      )

        User.objects.create_superuser('chris@gmail.com',
                                      'password',
                                      'chris',
                                      'drane',
                                      location=Location.objects.filter(zip_code='11104')[0],
                                      birth_date=date(1989,1,28)
                                      )
        return

    @staticmethod
    def create_reviews():
        reviewer = User.objects.all()[2]
        reviewee = User.objects.all()[0]
        x = Review(reviewer=reviewer,
                   reviewee=reviewee,
                   rating=3,
                   contents='terrible. This was the single worst gig buddy I have ever had.')
        x.save()


        reviewer = User.objects.all()[2]
        reviewee = User.objects.all()[0]
        x = Review(reviewer=reviewer,
                   reviewee=reviewee,
                   rating=5,
                   contents='Amazing')
        x.save()



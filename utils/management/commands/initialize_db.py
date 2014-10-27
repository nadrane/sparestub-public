# Standard Imports
import logging
from datetime import date
import datetime

# Django Imports
from django.core.management.base import BaseCommand
from django.core.management import call_command

# SpareStub Imports
from registration.models import User
from reviews.models import Review
from locations.models import Location
from tickets.models import Ticket


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Recreate the tables in the database according to our models
        call_command('empty_db', interactive=False)
        self.create_users()
        self.create_reviews()
        self.create_tickets()

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
    def create_tickets():
        Ticket.objects.create_ticket(poster=User.objects.get(pk=2),
                                     price=213.0,
                                     title='Dallas cowboys at Giants stadium this weekend! Looking for Dallas fans only!',
                                     start_datetime=datetime.datetime.today(),
                                     location_raw='Dallas, TX',
                                     location=Location.objects.filter(city='dallas')[0],
                                     ticket_type='S',
                                     payment_method='G',
                                     about='stuff stuff stuff dallas sucks stuff stuff stuff'
                                     )

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



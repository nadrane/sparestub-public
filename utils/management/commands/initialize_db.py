# Standard Imports
import logging
from datetime import date, timedelta

# Django Imports
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

# SpareStub Imports
from registration.models import User
from reviews.models import Review
from locations.models import Location, map_citystate_to_location
from tickets.models import Ticket


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Recreate the tables in the database according to our models
        call_command('empty_db', interactive=False)
        self.create_users()
        self.create_reviews()
        self.create_tickets()
        call_command('rebuild_index')

    @staticmethod
    def create_users():
        logging.debug('Creating user and person objects')
        # Create my user
        User.objects.create_superuser('nick@sparestub.com',
                                      'password',
                                      'nick',
                                      'drane',
                                      location=Location.objects.filter(zip_code='11102')[0],
                                      birth_date=date(1989, 1, 28),
                                      )

        User.objects.create_superuser('nick1@sparestub.com',
                                      'password',
                                      'andy',
                                      'drane',
                                      location=Location.objects.filter(zip_code='11103')[0],
                                      birth_date=date(1989, 1, 28),
                                      )

        User.objects.create_superuser('steph@sparestub.com',
                                      'password',
                                      'Stephanie',
                                      'MacConnell',
                                      location=Location.objects.filter(zip_code='11103')[0],
                                      birth_date=date(1988, 10, 30),

                                      )

        User.objects.create_superuser('stephanie2@sparestub.com',
                                      'password',
                                      'chris',
                                      'drane',
                                      location=Location.objects.filter(zip_code='11104')[0],
                                      birth_date=date(1989, 1, 28),

                                      )

        User.objects.create_superuser('smmacconnell@gmail.com',
                                      'password',
                                      'Jake',
                                      'Ham',
                                      location=Location.objects.filter(zip_code='94105')[0],
                                      birth_date=date(1989, 1, 28),

                                      )

        User.objects.create_superuser('drane128@gmail.com',
                                      'password',
                                      'George',
                                      'Apple',
                                      location=Location.objects.filter(zip_code='94111')[0],
                                      birth_date=date(1989, 1, 28),

                                      )

        User.objects.create_superuser('feed1@sparestub.com',
                                      'password',
                                      'Sally',
                                      'Swanson',
                                      location=Location.objects.filter(zip_code='73344')[0],
                                      birth_date=date(1988, 10, 30),

                                      )

        User.objects.create_superuser('feed2@sparestub.com',
                                      'password',
                                      'Bob',
                                      'Goldman',
                                      location=Location.objects.filter(zip_code='78701')[0],
                                      birth_date=date(1989, 1, 28),

                                      )

        User.objects.create_superuser('feed3@sparestub.com',
                                      'password',
                                      'Jenifer',
                                      'Suarez',
                                      location=Location.objects.filter(zip_code='33130')[0],
                                      birth_date=date(1989, 1, 28),

                                      )

        User.objects.create_superuser('feed10@sparestub.com',
                                      'password',
                                      'Maria',
                                      'Lopez',
                                      location=Location.objects.filter(zip_code='33128')[0],
                                      birth_date=date(1989, 1, 28),
                                      )

        User.objects.create_superuser('feed4@sparestub.com',
                                      'password',
                                      'Jay',
                                      'Britt',
                                      location=Location.objects.filter(zip_code='27615')[0],
                                      birth_date=date(1989, 1, 28),
                                      )

        User.objects.create_superuser('feed5@sparestub.com',
                                      'password',
                                      'Don',
                                      'MacLeod',
                                      location=Location.objects.filter(zip_code='27615')[0],
                                      birth_date=date(1989, 1, 28),

                                      )

        User.objects.create_superuser('feed6@sparestub.com',
                                      'password',
                                      'April',
                                      'Roman',
                                      location=Location.objects.filter(zip_code='27609')[0],
                                      birth_date=date(1989, 1, 28),

                                      )

        User.objects.create_superuser('feed7k@sparestub.com',
                                      'password',
                                      'Jack',
                                      'Richards',
                                      location=Location.objects.filter(zip_code='27622')[0],
                                      birth_date=date(1988, 10, 30),

                                      )
        return

    @staticmethod
    def create_tickets():
        # timedelta(weeks=40, days=84, hours=23, minutes=50, seconds=600)
        Ticket.objects.create_ticket(poster=User.objects.get(pk=2),
                                     price=213.0,
                                     title="Dallas cowboys at Giants stadium this weekend! Looking for Dallas fans only!",
                                     start_datetime=timezone.now() + timedelta(days=3, hours=1),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='S',
                                     payment_method='S',
                                     about='Come hang!',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=1),
                                     price=200.0,
                                     title='Dallas cowboys at Giants stadium. Great seats! Anyone welcome!',
                                     start_datetime=timezone.now() + timedelta(hours=7),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='S',
                                     payment_method='S',
                                     about='Going to a cookout beforehand you can join',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=3),
                                     price=175.0,
                                     title="Giant's/cowboys tickets in NYC. Looking for a fellow Giants fan. "
                                           "We're tailgating beforehand, and your welcome to join us.",
                                     start_datetime=timezone.now() + timedelta(days=17, hours=1),
                                     location_raw='Brooklyn, NY',
                                     location=map_citystate_to_location('Brooklyn', 'NY'),
                                     ticket_type='S',
                                     payment_method='G',
                                     about='Will be a good time',
                                     is_active=True,

                                     )


        Ticket.objects.create_ticket(poster=User.objects.get(pk=4),
                                     price=150.0,
                                     title="Friend bailed on me! Just ended up with 2 tickets to see the Giant's this weekend. "
                                           "Hit me up if you're ready to see Eli stomp on Romo.",
                                     start_datetime=timezone.now() + timedelta(days=80, hours=11),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='S',
                                     payment_method='G',
                                     about='dallas sucks amiright?!',
                                     is_active=True,

                                     )


        Ticket.objects.create_ticket(poster=User.objects.get(pk=1),
                                     price=35.0,
                                     title="Ben Howard at MHW",
                                     start_datetime=timezone.now() + timedelta(days=30, hours=1),
                                     location_raw='Brooklyn, NY',
                                     location=map_citystate_to_location('Brooklyn', 'NY'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='Super excited to see Ben Howard at the Music Hall of Williamsburg. He is'
                                           'my favorite artist and I would love a partner in crime!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=2),
                                     price=130.0,
                                     title="KATY PERRY TICKET- Friend bailed on me! Ugh!!",
                                     start_datetime=timezone.now() + timedelta(days=30, hours=1),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='M',
                                     payment_method='S',
                                     about='Madison Sq Gardens',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=3),
                                     price=300.0,
                                     title="Book of Mormon ticket available",
                                     start_datetime=timezone.now() + timedelta(days=3, hours=20),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='T',
                                     payment_method='S',
                                     about='My mom was supposed to come into town but can no longer make it... so I '
                                           'have this extra Book of Mormon ticket. Great seats.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=4),
                                     price=40.0,
                                     title="The Fray, Oh Honey opener in Brooklyn",
                                     start_datetime=timezone.now() + timedelta(days=6, hours=22),
                                     location_raw='Brooklyn, NY',
                                     location=map_citystate_to_location('Brooklyn', 'NY'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='The Fray is cool but especially going to see Oh Honey.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=1),
                                     price=25.0,
                                     title="Mozart The Magic Flute Met Opera orchestra seats",
                                     start_datetime=timezone.now() + timedelta(days=1, hours=20),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='T',
                                     payment_method='S',
                                     about='Great seats, only $25, friend had to travel for work.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=2),
                                     price=80.0,
                                     title="Mario Lopez comedy show VIP section",
                                     start_datetime=timezone.now() + timedelta(days=10, hours=1),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='C',
                                     payment_method='S',
                                     about='Our own table up front',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=3),
                                     price=100.0,
                                     title="Katt Williams in Madison Sq Garden",
                                     start_datetime=timezone.now() + timedelta(days=7, hours=20),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='C',
                                     payment_method='G',
                                     about='Funniest man alive. Section 3G Row 17 Seats 3 and 4',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=4),
                                     price=370.0,
                                     title="Jay Z and Beyonce.... IT IS FINALLY HAPPENING. Experience it with me.",
                                     start_datetime=timezone.now() + timedelta(days=32, hours=1),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='M',
                                     payment_method='S',
                                     about='Third row seats... looking for another lover of Queen Bey and our NY boy',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=1),
                                     price=70.0,
                                     title="Girlfriend broke up with me- want to see a play? The Lion King",
                                     start_datetime=timezone.now() + timedelta(days=11, hours=13),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='T',
                                     payment_method='G',
                                     about='Have two tickets to the Lion King I bought for my girlfriend for her'
                                           'birthday but then she broke up with me... Soo, if you want to see it '
                                           'with me and help heal my broken heart, we have pretty good seats.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=2),
                                     price=70.0,
                                     title="Kenny Chesney at the Barclay Center",
                                     start_datetime=timezone.now() + timedelta(days=12, hours=16),
                                     location_raw='Brooklyn, NY',
                                     location=map_citystate_to_location('Brooklyn', 'NY'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='Cowboy hats and cowboy boots are required!! Going to tailgate beforehand. '
                                           'Bring your drinking and your dancing shoes. We will have corn hole!',
                                     is_active=True,

                                     )
        Ticket.objects.create_ticket(poster=User.objects.get(pk=3),
                                     price=290.0,
                                     title="The Heat Are Coming To Town...",
                                     start_datetime=timezone.now() + timedelta(days=30, hours=19),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='S',
                                     payment_method='S',
                                     about='Courtside seats. 2 extra available. Want to get there at least an hour'
                                           'early.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=4),
                                     price=150.0,
                                     title="Bruce Springsteen two extra GA tickets",
                                     start_datetime=timezone.now() + timedelta(days=38, hours=20),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='We love Bruce! My husband and I have two extra tickets to see Bruce and'
                                           'we love meeting new people. Come along!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=1),
                                     price=80.0,
                                     title="Yankees showcase tickets",
                                     start_datetime=timezone.now() + timedelta(days=2, hours=12),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='S',
                                     payment_method='S',
                                     about='Section 17 Row 3 Seats 14-15. Going with a small group of about 6 friends.'
                                           'Would be great if you want to join.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=2),
                                     price=90.0,
                                     title="Lady Gaga in Madison Square Garden",
                                     start_datetime=timezone.now() + timedelta(days=20, hours=19),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='One extra ticket to see Lady Gaga- row 20 section 10',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=3),
                                     price=70.0,
                                     title="Frozen on Ice- want to join me?",
                                     start_datetime=timezone.now() + timedelta(days=6, hours=17),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='T',
                                     payment_method='G',
                                     about='Call me cheesy, but I would love to see Frozen on ice. I have no girlfriend'
                                           'so just trying to find someone to go with.',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=4),
                                     price=70.0,
                                     title="Frozen On Ice- 1 ticket",
                                     start_datetime=timezone.now() + timedelta(days=6, hours=17),
                                     location_raw='New York, NY',
                                     location=map_citystate_to_location('New York', 'NY'),
                                     ticket_type='T',
                                     payment_method='S',
                                     about='I love Frozen! My friend had to go out of town on business so I have an'
                                           'extra ticket. Team Elsa!',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=5),
                                     price=70.0,
                                     title="Frozen on Ice extra ticket",
                                     start_datetime=timezone.now() + timedelta(days=9, hours=17),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='T',
                                     payment_method='S',
                                     about='I looooooooove Frozen! Friend had to go out of town on business so I have'
                                           'an extra ticket. Team Oloff!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=5),
                                     price=160.0,
                                     title="My friend bailed last minute! Anyone want to go to the 49ers game with me?",
                                     start_datetime=timezone.now() + timedelta(days=2, hours=20),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='S',
                                     payment_method='G',
                                     about='We have pretty good seats, section 32 row 12 seats 16-17. Want to do some'
                                           'tailgating beforehand if you are down.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=5),
                                     price=220.0,
                                     title="49ers BOX SEAT ticket available",
                                     start_datetime=timezone.now() + timedelta(days=2, hours=20),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='S',
                                     payment_method='S',
                                     about='My friends and I are splitting a box for the game this weekend 4 ways. One'
                                           'of our friends can no longer go so his seat is up for grabs!',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=5),
                                     price=175.0,
                                     title="San Francisco 49ers vs. Detroit Lions this weekend",
                                     start_datetime=timezone.now() + timedelta(days=2, hours=20),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='S',
                                     payment_method='G',
                                     about='Got tickets, got dumped. Anybody cool looking to go to the game?',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=6),
                                     price=195.0,
                                     title="Katy Perry in concert in February, third row seat",
                                     start_datetime=timezone.now() + timedelta(days=4, hours=10),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='M',
                                     payment_method='S',
                                     about='Third row seats in section 2, going with a few girlfriends and one of them'
                                           'can no longer go. We love to have a good time and would love to get to'
                                           'know a new friend!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=6),
                                     price=65.0,
                                     title="JOHN MAYER SHOW TONIGHT extra ticket",
                                     start_datetime=timezone.now() + timedelta(days=0, hours=12),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='Friend bailed and I still really want to go see John Mayer. Send me a'
                                           'message if you want to go- I will bring anyone!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=6),
                                     price=15.0,
                                     title="F.Stokes at UCSF",
                                     start_datetime=timezone.now() + timedelta(days=3, hours=12),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='F.Stokes is coming to UCSF and I bought two tickets thinking my friend'
                                           'could go with me. She bailed so it is available! GA ticket',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=6),
                                     price=40.0,
                                     title="Dane Cook at The Punch Line comedy club next week",
                                     start_datetime=timezone.now() + timedelta(days=5, hours=18),
                                     location_raw='San Francisco, CA',
                                     location=map_citystate_to_location('San Francisco', 'CA'),
                                     ticket_type='C',
                                     payment_method='S',
                                     about='I have two tickets to the Dane Cook show next week and my buddy can no'
                                           'longer go with me. His ticket is up for sale. Would be cool to get'
                                           'dinner beforehand if you want to.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=7),
                                     price=70.0,
                                     title="FROZEN! ON! ICE!",
                                     start_datetime=timezone.now() + timedelta(days=30, hours=1),
                                     location_raw='Austin, TX',
                                     location=map_citystate_to_location('Austin', 'TX'),
                                     ticket_type='T',
                                     payment_method='S',
                                     about='I have two tickets and would love to make a new friend this weekend.'
                                           'Message me if you are interested!',
                                     is_active=True,

                                    )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=7),
                                     price=20.0,
                                     title="Keeping It Weird. Comedy show, next week. You in?",
                                     start_datetime=timezone.now() + timedelta(days=30, hours=1),
                                     location_raw='Austin, TX',
                                     location=map_citystate_to_location('Austin', 'TX'),
                                     ticket_type='C',
                                     payment_method='G',
                                     about='Awesome show going on at Last Gas comedy club. I bought two tickets and'
                                           'figured somebody on here would want to come. It is a riot. Come have some'
                                           'fun with me!',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=7),
                                     price=800.0,
                                     title="Extra SXSW Interactive Badge- join me at SXSW!",
                                     start_datetime=timezone.now() + timedelta(days=40, hours=1),
                                     location_raw='Austin, TX',
                                     location=map_citystate_to_location('Austin', 'TX'),
                                     ticket_type='O',
                                     payment_method='S',
                                     about='SXSW (South by Southwest) in Austin is a huge event. I have an extra '
                                           'Interactive Badge that I got with my company discount to bring someone '
                                           'interested in the event or the presenters. Come join me for a fun few days!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=8),
                                     price=70.0,
                                     title="Talking Heads at Armadillo World HQ",
                                     start_datetime=timezone.now() + timedelta(days=11, hours=10),
                                     location_raw='Austin, TX',
                                     location=map_citystate_to_location('Austin', 'TX'),
                                     ticket_type='S',
                                     payment_method='G',
                                     about='One extra GA ticket',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=9),
                                     price=70.0,
                                     title="Frozen on ice",
                                     start_datetime=timezone.now() + timedelta(days=12, hours=10),
                                     location_raw='Miami, FL',
                                     location=map_citystate_to_location('Miami', 'FL'),
                                     ticket_type='T',
                                     payment_method='G',
                                     about='Extra frozen ticket should be fun come along!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=9),
                                     price=55.0,
                                     title="Pitbull concert 1 extra ticket",
                                     start_datetime=timezone.now() + timedelta(days=12, hours=16),
                                     location_raw='Miami, FL',
                                     location=map_citystate_to_location('Miami', 'FL'),
                                     ticket_type='M',
                                     payment_method='S',
                                     about='Section 14 Row 2 seats 4-5',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=9),
                                     price=450.0,
                                     title="Holy Ship Weekend 1 extra ticket",
                                     start_datetime=timezone.now() + timedelta(days=18, hours=1),
                                     location_raw='Miami, FL',
                                     location=map_citystate_to_location('Miami', 'FL'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='Standard Window, weekend 1, $450',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=10),
                                     price=600.0,
                                     title="Holy Ship weekend 1 large balcony",
                                     start_datetime=timezone.now() + timedelta(days=18, hours=1),
                                     location_raw='Miami, FL',
                                     location=map_citystate_to_location('Miami', 'FL'),
                                     ticket_type='M',
                                     payment_method='S',
                                     about='Large Balcony room during Holy Ship weekend 1. AMAZING TIME guaranteed!',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=10),
                                     price=370.0,
                                     title="Weekend 1 HOLY SHIP",
                                     start_datetime=timezone.now() + timedelta(days=18, hours=1),
                                     location_raw='Miami, FL',
                                     location=map_citystate_to_location('Miami', 'FL'),
                                     ticket_type='M',
                                     payment_method='S',
                                     about='Standard room, amazing lineup. Friend bailed, I have an extra ticket.',
                                     is_active=True,

                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=11),
                                     price=60.0,
                                     title="Keith Urban at Walnut Creek 2 lawn seats available",
                                     start_datetime=timezone.now() + timedelta(days=10, hours=10),
                                     location_raw='Raleigh, NC',
                                     location=map_citystate_to_location('Raleigh', 'NC'),
                                     ticket_type='M',
                                     payment_method='S',
                                     about='Lawn seats, gonna play some games in the parking lot beforehand! Two tickets'
                                           'available to go to the concert with my friend and I',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=11),
                                     price=30.0,
                                     title="Carlos Mencia at Goodnight's comedy club",
                                     start_datetime=timezone.now() + timedelta(days=3, hours=16),
                                     location_raw='Raleigh, NC',
                                     location=map_citystate_to_location('Raleigh', 'NC'),
                                     ticket_type='C',
                                     payment_method='G',
                                     about='I have two tickets to Carlos Mencia- my work friend was supposed to go with'
                                           'me but cannot go anymore. Would also like to grab dinner before the show.',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=11),
                                     price=75.0,
                                     title="Carolina Hurricanes hockey - extra ticket section 12 row 4",
                                     start_datetime=timezone.now() + timedelta(days=30, hours=1),
                                     location_raw='Raleigh, NC',
                                     location=map_citystate_to_location('Raleigh', 'NC'),
                                     ticket_type='S',
                                     payment_method='G',
                                     about='Friend is not able to go anymore so looking for a buddy to go with.',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=12),
                                     price=275.0,
                                     title="Carolina Panthers game next Sunday, BOX SEATS",
                                     start_datetime=timezone.now() + timedelta(days=6, hours=17),
                                     location_raw='Charlotte, NC',
                                     location=map_citystate_to_location('Charlotte', 'NC'),
                                     ticket_type='S',
                                     payment_method='S',
                                     about='Box seats on the Panthers side, split the box with 5 friends. Should be a'
                                           'really good time!',
                                     is_active=True,
                                     )


        Ticket.objects.create_ticket(poster=User.objects.get(pk=13),
                                     price=95.0,
                                     title="UNC Men's basketball vs Duke 9th row",
                                     start_datetime=timezone.now() + timedelta(days=2, hours=1),
                                     location_raw='Raleigh, NC',
                                     location=map_citystate_to_location('Raleigh', 'NC'),
                                     ticket_type='S',
                                     payment_method='G',
                                     about='Watch the Tarheels destroy the dookies from the 9th row with me. A friend'
                                           'was originally supposed to go, but is not able to anymore. More fun for us!',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=13),
                                     price=35.0,
                                     title="The Fray and Oh Honey at Red Hat Amphitheater",
                                     start_datetime=timezone.now() + timedelta(days=3, hours=16),
                                     location_raw='Raleigh, NC',
                                     location=map_citystate_to_location('Raleigh', 'NC'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='Red Hat is an outdoor amphitheater. Oh Honey is the opener but they are'
                                           'awesome. Would like to get dinner beforehand and maybe drinks after?',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=13),
                                     price=70.0,
                                     title="Frozen on Ice extra ticket need a friend!",
                                     start_datetime=timezone.now() + timedelta(days=14, hours=10),
                                     location_raw='Raleigh, NC',
                                     location=map_citystate_to_location('Raleigh', 'NC'),
                                     ticket_type='T',
                                     payment_method='S',
                                     about='TEAM ELSA!! My friend bailed so I have an extra ticket in 2wks.',
                                     is_active=True,
                                     )

        Ticket.objects.create_ticket(poster=User.objects.get(pk=14),
                                     price=70.0,
                                     title="Rascal Flatts extra lawn seat ticket",
                                     start_datetime=timezone.now() + timedelta(days=30, hours=16),
                                     location_raw='Raleigh, NC',
                                     location=map_citystate_to_location('Raleigh', 'NC'),
                                     ticket_type='M',
                                     payment_method='G',
                                     about='Extra ticket, BYO blanket!',
                                     is_active=True,
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



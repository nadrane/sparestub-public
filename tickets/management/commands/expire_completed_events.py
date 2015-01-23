from tickets.tasks import expire_completed_events
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Identify ticket whose event date and time has passed and mark them with an appropriate new status. ' \
           'Also mark all expired requests for this ticket with a status of closed.'

    def handle(self, *args, **options):
        # Do this as a command until we are willing to pay for a celery beat dyno and can just use the tasks.py.
        expire_completed_events()
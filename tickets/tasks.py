# Standard Imports
import logging
from datetime import timedelta

#3rd Party Imports
from celery.task import periodic_task

# Django Imports
from django.core.management import call_command

# Module Imports
from .models import Ticket

#@periodic_task(run_every=timedelta(minutes=1))
def expire_completed_events():
    """
    Identify ticket whose event date and time has passed and mark them with an appropriate new status.
    Also mark all expired requests for this ticket with a status of closed.
    """

    for ticket_to_expire in Ticket.completed_but_not_expired():
        logging.debug('Marking ticket {} as expired'.format(ticket_to_expire.id))
        ticket_to_expire.change_status('E')

#@periodic_task(run_every=timedelta(minutes=1))
def recompute_ticket_index():

    # Age is in hours. It tells update_index the start date to begin indexing within begins an hour ago.
    # We are not allowed to do less than an hour (like 15 minutes) or anything that is not a multiple of hours.
    call_command('update_index', age=1)
# Standard Imports
import datetime
import logging

# Django Imports
from utils.models import TimeStampedModel
from django.db import models
from django.template.loader import render_to_string
from django.db import transaction
from django.db.models import Q

# SparStub imports
from registration.models import User
from tickets.models import Ticket
from messages.models import Message
from utils.email import send_email
from stripe_data.models import Card

# Module Imports
from .settings import request_model_settings,\
    REQUEST_SENT_SUBJECT, REQUEST_SENT_TEMPLATE,\
    REQUEST_RECEIVED_SUBJECT, REQUEST_RECEIVED_TEMPLATE, \
    REQUEST_INACTIVE_SUBJECT, REQUEST_INACTIVE_TEMPLATE, \
    REQUEST_ACCEPTED_SUBJECT, REQUEST_ACCEPTED_TEMPLATE, \
    REQUEST_CANCELLED_TO_SELLER_SUBJECT, REQUEST_CANCELLED_TO_SELLER_TEMPLATE


class RequestManager(models.Manager):

    def create_request(self, ticket, requester):
        """
        Creates a request record using the given input.
        This function will shoot off an email to both the ticket poster and the user that requested to buy the ticket.
        """

        request = self.model(requester=requester,
                             ticket=ticket,
                             status='P'
                             )
        request.save()

        logging.info('Request created: {}'.format(repr(request)))

        poster = ticket.poster

        poster.send_mail(REQUEST_RECEIVED_SUBJECT,
                         '',
                         REQUEST_RECEIVED_TEMPLATE,
                         {'user': requester,
                          'ticket': ticket
                          }
                         )

        requester.send_mail(REQUEST_SENT_SUBJECT,
                            '',
                            REQUEST_SENT_TEMPLATE,
                            {'user': requester,
                             'ticket': ticket
                             }
                            )

        message_body = 'This is an automated message to let you know that {} has requested to buy your ticket. ' \
                       'Sellers have 48 hours to respond by clicking either the Accept or Decline button at the ' \
                       'top of the screen'.format(requester.first_name.title())

        # No need to send an email that a message was sent since we just sent an email about the request
        Message.objects.create_message(requester, poster, ticket, message_body, False)

        return request


class Request(TimeStampedModel):
    """
    Created when a user requests to buy a ticket. This model represents that action.
    """

    requester = models.ForeignKey(User,
                                  blank=False,
                                  null=False,
                                  )

    ticket = models.ForeignKey(Ticket,
                               blank=False,
                               null=False
                               )

    status = models.CharField(max_length=1,
                              null=False,
                              blank=False,
                              choices=request_model_settings.get('REQUEST_STATUSES'),
                              )

    card = models.ForeignKey(Card,
                             null=False,
                             blank=False,
                             )

    objects = RequestManager()

    def __repr__(self):
        return '{class_object} - {id} \n' \
               'requester: {requester} \n' \
               'ticket: {ticket}'\
               .format(class_object=self.__class__,
                       id=self.id,
                       requester=repr(self.requester),
                       ticket=repr(self.ticket))

    def calculate_expiration_datetime(self):
        return self.creation_timestamp + datetime.timedelta(hours=48)

    def accept(self):
        """
        When a seller accepts a user's request and agrees to go to the show with them.
        """
        ticket = self.ticket
        poster = ticket.poster
        requester = self.requester

        # Make sure that the ticket and request are updated in tandem
        with transaction.atomic():
            #TODO make sure atomic transactions does not cause this ticket to change it's status to 'S' instead of 'A' inside change_status
            self.status = 'A'
            self.save()
            ticket.change_status('S')

        Message.objects.create_message(poster, requester, ticket,
                                       "This is an automated message: Congratulations,the request was accepted! Check your email for next steps.", False)

        send_email([poster.email, requester.email],
                   REQUEST_ACCEPTED_SUBJECT,
                   '',
                   REQUEST_ACCEPTED_TEMPLATE,
                   ticket=ticket
                   )

    def decline(self):
        """
        When a seller declines to go to an event with a user
        """
        self.status = 'D'
        self.save()

        requester = self.requester
        ticket = self.ticket
        poster = ticket.poster

        Message.objects.create_message(poster, requester, ticket,
                                       "This is an automated message. "
                                       "The bad news: your request was declined. "
                                       "The good news: there are plenty of stubs in the sea.",
                                       False)

        self.requester.send_mail(REQUEST_INACTIVE_SUBJECT,
                                 '',
                                 REQUEST_INACTIVE_TEMPLATE,
                                 user=requester,
                                 ticket=ticket)

    def ticket_cancelled(self):
        """
        This happens when a ticket is deactivated. It changes the status of the request to 'T - Ticket Cancelled'
        This function will send emails to inform the requester that the ticket was cancelled.
        It will also send an automated message that explains that the message was cancelled
        """

        requester = self.requester
        ticket = self.ticket

        self.requester.send_mail(REQUEST_INACTIVE_SUBJECT,
                                 '',
                                 REQUEST_INACTIVE_TEMPLATE,
                                 user=requester,
                                 ticket=ticket
                                 )

        message_body = 'This is an automated message to let you know that {}' \
                       ' has cancelled this ticket.'.format(ticket.poster.first_name.title())

        # No need to send an email that a message was sent since we just sent an email about the request
        Message.objects.create_message(ticket.poster, self.requester, ticket, message_body, False)

        self.status = 'T'
        self.save()

    def cancel(self):
        """
        Cancel a request. This happens when a user rescinds their request to buy a ticket.
        The status of the ticket will be changed to 'C'
        This function will send emails to inform the requester that the ticket was cancelled.
        It will also send an automated message that explains that the message was cancelled
        """

        ticket = self.ticket
        poster = ticket.poster
        requester = self.requester
        self.status = 'C'
        self.save()

        requester.send_mail(REQUEST_INACTIVE_SUBJECT,
                            '',
                            REQUEST_INACTIVE_SUBJECT,
                            user=requester,
                            ticket=ticket
                            )

        message_body = render_to_string(REQUEST_CANCELLED_TO_SELLER_TEMPLATE,
                                        {'requester': requester, 'ticket': ticket})
        poster.send_mail(REQUEST_CANCELLED_TO_SELLER_SUBJECT,
                         '',
                         REQUEST_CANCELLED_TO_SELLER_TEMPLATE,
                         requester=requester,
                         ticket=ticket
                         )

        message_body = 'This is an automated message to let you know that {}' \
                       ' has cancelled their request.'.format(requester.first_name.title())

        # No need to send an email that a message was sent since we just sent an email about the request
        Message.objects.create_message(poster, requester, ticket, message_body, False)

    @staticmethod
    def get_last_request(user, ticket):
        """
        Get the request for a given requester ticket combination
        Note that there can be multiple requests for a ticket/user combination if a request was cancelled by the user
        or if a request expired.
        """
        request = Request.objects.filter(requester=user, ticket=ticket).order_by('-creation_timestamp')
        if request:
            return request[0]
        return None

    @staticmethod
    def get_all_requests(user, ticket):
        """
        Return all requests of a particular user for this ticket.
        There may be more than 1 if
            1. The ticket expired and the user requested
            2. The user cancelled his request and then re-requested
        """
        return Request.objects.filter(requester=user, ticket=ticket)

    @staticmethod
    def requested_other_ticket_same_time(user, ticket):
        """
        Returns True or False, representing whether a user has requested to buy ANY ticket that starts at or within 2
        hours of the time of the inputted ticket. Incidentally, this query also tells us if the user has requested the
        inputted ticket.
        """
        ticket_start_datetime = ticket.start_datetime
        early_bound = ticket_start_datetime + datetime.timedelta(hours=2)
        late_bound = ticket_start_datetime - datetime.timedelta(hours=2)

        # We want all tickets by this user that
        # 1. Start on the same date as the inputted ticket
        # 2. begin within 2 hours of the start time of the inputted ticket
        return Request.objects.filter(requester=user,
                                      ticket__status='P',
                                      ticket__start_date=ticket.start_date,
                                      ticket__start_datetime__lte=early_bound,
                                      ticket__start_datetime__gte=late_bound) \
                                      .exclude(ticket=ticket)\
                                      .exists()

    @staticmethod
    def can_request(ticket, user):
        """
        Can the inputted user send a request for this ticket
        """
        can_request = None

        if ticket.is_requestable():
            # If the user has a pending request open or has a declined request, he cannot request again
            if Request.get_all_requests(user, ticket).filter(Q(status='P') | Q(status='D')).exists():
                can_request = False
            else:
                can_request = True
        else:
            can_request = False

        return can_request

    @staticmethod
    def has_requested(ticket, user):
        """
        Returns a boolean value indicated whether an inputted user has requested to buy an inputted ticket.
        """

        return Request.objects.filter(ticket=ticket, requester=user, status='P').exists()
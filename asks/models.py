# Standard Imports
import datetime

# Django Imports
from utils.models import TimeStampedModel
from django.db import models
from django.template.loader import render_to_string

# SparStub imports
from registration.models import User
from tickets.models import Ticket
from messages.models import Message

# Module Imports
from .settings import request_model_settings, TICKET_REQUESTED_REQUESTER_SUBJECT, \
    TICKET_REQUESTED_REQUESTER_TEMPLATE, TICKET_REQUESTED_POSTER_SUBJECT, TICKET_REQUESTED_POSTER_TEMPLATE, \
    TICKET_CANCELLED_SUBJECT, TICKET_CANCELLED_TEMPLATE


class RequestManager(models.Manager):

    def create_request(self, ticket, requester):
        """
        Creates a request record using the given input.
        This function will shoot off an email to both the ticket poster and the user that requested to buy the ticket.
        """

        # There are only a few cirucmstances where a user can submit 2 requests for a single ticket.
        #   1.  If the user cancels their own request, it should be okay for them to re-request
        #   2.  If a ticket expires, but the request was not declined, the buyer can re-request
        if Request.objects.filter(requester=requester, ticket=ticket).exclude(status='E').exclude(status='C'):
            return None

        request = self.model(requester=requester,
                             ticket=ticket,
                             status='P'
                             )
        request.save()

        poster = ticket.poster

        poster.send_mail(TICKET_REQUESTED_POSTER_SUBJECT,
                         message='',
                         html=render_to_string(TICKET_REQUESTED_POSTER_TEMPLATE)
                         )

        requester.send_mail(TICKET_REQUESTED_REQUESTER_SUBJECT,
                            message='',
                            html=render_to_string(TICKET_REQUESTED_REQUESTER_TEMPLATE)
                            )

        message_body = 'This is an automated message to let you know that {} has requested to buy your ticket. ' \
                       'You have 48 to respond by clicking one of the buttons at the top ' \
                       'of the screen'.format(requester.first_name.title())

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
                              default='',
                              choices=request_model_settings.get('REQUEST_STATUSES'),
                              )

    objects = RequestManager()

    def cancel(self):
        """
        Cancel a request. This happens when a ticket is deactivated.
        The status will actually be changed in tickes.models.Ticket.deactivate because we can update all the request
        statuses in bulk.
        This function will send emails to inform the requester that the ticket was cancelled.
        It will also send an automated message that explains that the message was cancelled
        """

        self.requester.send_mail(TICKET_CANCELLED_SUBJECT,
                                 message='',
                                 html=render_to_string(TICKET_CANCELLED_TEMPLATE))
        ticket = self.ticket

        message_body = 'This is an automated message to let you know that {}' \
                       ' has cancelled this ticket.'.format(ticket.poster.first_name.title())

        # No need to send an email that a message was sent since we just sent an email about the request
        Message.objects.create_message(ticket.poster, self.requester, ticket, message_body, False)

    @staticmethod
    def get_request(user, ticket):
        """
        Get the request for a given requester ticket combination
        Note that there can be multiple requests for a ticket/user combination if a request was cancelled by the user
        or if a request expired.
        """
        request = Request.objects.filter(requester=user, ticket=ticket).order_by('creation_timestamp')
        if request:
            return request[0]
        return None

    @staticmethod
    def requests_for_ticket(user, ticket):
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
                                      ticket__is_active=True,
                                      ticket__start_date=ticket.start_date,
                                      ticket__start_datetime__lte=early_bound,
                                      ticket__start_datetime__gte=late_bound) \
                                      .exclude(ticket=ticket)\
                                      .exists()

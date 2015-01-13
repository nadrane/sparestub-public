# Standard Imports
import datetime

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

        poster = ticket.poster

        received_html_message = render_to_string(REQUEST_RECEIVED_TEMPLATE,
                                                 {'user': requester,
                                                  'ticket': ticket
                                                  })
        poster.send_mail(REQUEST_RECEIVED_SUBJECT,
                         message='',
                         html=received_html_message
                         )

        send_html_message = render_to_string(REQUEST_SENT_TEMPLATE,
                                             {'user': requester,
                                              'ticket': ticket
                                              })
        requester.send_mail(REQUEST_SENT_SUBJECT,
                            message='',
                            html=send_html_message
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

    def calculate_expiration_datetime(self):
        return self.creation_timestamp + datetime.timedelta(hours=48)

    def accept(self):
        """
        When a seller accepts a user's request and agrees to go to the show with them.
        """
        import pdb
        pdb.set_trace()

        ticket = self.ticket
        poster = ticket.poster
        requester = self.requester

        # Make sure that the ticket and request are updated in tandem
        with transaction.atomic():
            #TODO make sure atomic transactions does not cause this ticket to change it's status to 'S' instead of 'A' inside change_status
            self.status = 'A'
            self.save()
            ticket.change_status('S')

        message_body = render_to_string(REQUEST_ACCEPTED_TEMPLATE,
                                        {'ticket': ticket})

        poster.send_mail(REQUEST_ACCEPTED_SUBJECT,
                         message='',
                         html=message_body
                         )

        requester.send_mail(REQUEST_ACCEPTED_SUBJECT,
                            message='',
                            html=message_body
                            )

    def decline(self):
        """
        When a seller declines to go to an event with a user
        """
        self.status = 'D'
        self.save()

        message_body = render_to_string(REQUEST_INACTIVE_TEMPLATE,
                                        {'user': self.requester,
                                         'ticket': self.ticket})
        self.requester.send_mail(REQUEST_INACTIVE_SUBJECT,
                                 message='',
                                 html=message_body)

    def cancel(self):
        """
        Cancel a request. This happens when a ticket is deactivated.
        The status will actually be changed in tickes.models.Ticket.deactivate because we can update all the request
        statuses in bulk.
        This function will send emails to inform the requester that the ticket was cancelled.
        It will also send an automated message that explains that the message was cancelled
        """

        self.requester.send_mail(REQUEST_INACTIVE_SUBJECT,
                                 message='',
                                 html=render_to_string(REQUEST_INACTIVE_TEMPLATE))
        ticket = self.ticket

        message_body = 'This is an automated message to let you know that {}' \
                       ' has cancelled this ticket.'.format(ticket.poster.first_name.title())

        # No need to send an email that a message was sent since we just sent an email about the request
        Message.objects.create_message(ticket.poster, self.requester, ticket, message_body, False)

    @staticmethod
    def get_last_request(user, ticket):
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
# Django Imports
from django.db import models

# SpareStub Imports
from utils.models import TimeStampedModel
from registration.models import User
from tickets.models import Ticket


class Message(TimeStampedModel):
    """
    A single exchange between two users. A set of messages related to a specific ticket constitutes a conversation
    """
    sender = models.ForeignKey(User,
                               blank=False,
                               null=False,
                               related_name='sender',
                               )

    receiver = models.ForeignKey(User,
                                 blank=False,
                                 null=False,
                                 related_name='receiver',
                                 )

    body = models.TextField(max_length=10000)

    is_read = models.BooleanField(blank=False,
                                  null=False,
                                  default=False)

    datetime_read = models.DateTimeField(blank=True,
                                         null=True,
                                         default=None)


class Conversation(models.Model):
    """
    Just a collection of messages between two users for a particular ticket
    """
    messages = models.ForeignKey(Message,
                                 blank=False,
                                 null=False,
                                 )

    ticket = models.ForeignKey(Ticket,
                               blank=False,
                               null=False
                               )
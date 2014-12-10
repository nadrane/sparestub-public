# Django Imports
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string

# SpareStub Imports
from utils.models import TimeStampedModel
from registration.models import User
from tickets.models import Ticket
from .settings import message_model_settings, new_message_subject, new_message_template


class MessageManager(models.Manager):

    def create_message(self, sender, receiver, ticket, body):
        """
        Creates a message record using the given input.
        """

        message = self.model(sender=sender,
                             receiver=receiver,
                             ticket=ticket,
                             body=body,
                             is_read=False,
                             datetime_read=None,
                             is_active=True,
                             )

        receiver.send_mail(new_message_subject,
                           render_to_string(new_message_template),
                           )


        message.save(using=self._db)

        return message


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

    ticket = models.ForeignKey(Ticket,
                               blank=False,
                               null=False
                               )

    body = models.TextField(max_length=message_model_settings.get('BODY_MAX_LENGTH'))

    is_read = models.BooleanField(blank=False,
                                  null=False,
                                  default=False)

    datetime_read = models.DateTimeField(blank=True,
                                         null=True,
                                         default=None)

    # Does this message belong to an active conversation about a ticket that has not yet been sold?
    # TODO probably should mark conversation inactive on rejection
    is_active = models.BooleanField(blank=False,
                                    null=False,
                                    default=False
                                    )

    objects = MessageManager()

    def __str__(self):
        return '{}: {} -> {}\n'.format(self.id, self.sender, self.receiver)

    @staticmethod
    def messages_received(user):
        """
        Returns a QuerySet of all messages the user has received.
        """

        return Message.objects.filter(conversation__receiver=user)

    @staticmethod
    def messages_sent(user):
        """
        Returns a QuerySet of all messages the user has sent.
        """

        return Message.objects.filter(conversation__sender=user)

    @staticmethod
    def all_messages(user):
        """
        Returns a QuerySet of all conversations this user is involved in
        """

        return Message.objects.filter(Q(sender=user) | Q(receiver=user))

    def last_message_time(self):
        """
        Returns the time between now and the time the last message was sent for a particular conversation
        """

        messages = Message.objects.filter(conversation=self.id).order_by('creation_timestamp')
        if messages:
            return messages[0].creation_timestamp
        return None

    @staticmethod
    def get_messages_in_conversation(user1, user2, ticket):
        """
        A conversation is defined as a set of messages with a unique sender, receiver, and ticket combination.
        Basically, it's an exchange between two users about a given ticket.
        """

        # Note that both users may function as both the sender and the receiver. After all, they will both send
        # and receive messages in a conversation (hopefully).
        return Message.objects.filter(ticket=ticket)\
                              .filter((Q(sender=user1) & Q(receiver=user2)) |
                                       Q(sender=user2) & Q(receiver=user1))

    @staticmethod
    def get_messages_received(user):
        """
        Returns a QuerySet of messages where the inputted user was the receiver
        """

        # Note that both users may function as both the sender and the receiver. After all, they will both send
        # and receive messages in a conversation (hopefully).
        return Message.objects.filter(receiver=user)

    @staticmethod
    def get_all_messages_sorted(user):
        """
        Returns a QuerySet of messages that are grouped according to the above definition of a conversation for a
        particular user.
        """

        return Message.all_messages(user).order_by('ticket', '-creation_timestamp')

    @staticmethod
    def message_count(user):
        """
        Get the total number of unread messages for a given user.
        """

        return Message.objects.filter(receiver=user.id).filter(is_read=False).count()


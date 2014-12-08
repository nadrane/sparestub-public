# Django Imports
from django.db import models
from django.db import transaction

# SpareStub Imports
from utils.models import TimeStampedModel
from registration.models import User
from tickets.models import Ticket
from .settings import message_model_settings


class ConversationManager(models.Manager):

    def create_conversation(self, sender, receiver, ticket):
        """
        Creates a conversation between two users and a ticket. It is a collection of messages. There shouldn't be a
        reason to call this outside of create_message.
        """

        conversation = self.model(sender=sender,
                                  receiver=receiver,
                                  ticket=ticket
                                  )

        conversation.save(using=self._db)

        return conversation


class Conversation(TimeStampedModel):
    """
    Just a collection of messages between two users for a particular ticket
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

    objects = ConversationManager()

    @staticmethod
    def conversations_received(user):
        return Conversation.objects.filter(receiver=user)

    @staticmethod
    def conversations_started(user):
        return Conversation.objects.filter(sender=user)


class MessageManager(models.Manager):

    #@transaction.atomic()  # Keep this atomic so that messages and conversations are always created together.
    def create_message(self, sender, receiver, ticket, body):
        """
        Creates a message record using the given input. If the conversation does not already exists between these
        two users for this particular ticket, a conversation is created as well.
        """

        conversation = Conversation.objects.filter(sender=sender, receiver=receiver, ticket=ticket)

        if not conversation:
            conversation = Conversation.objects.create_conversation(sender, receiver, ticket)
        else:
            conversation = conversation[0]

        message = self.model(conversation=conversation,
                             body=body,
                             is_read=False,
                             datetime_read=None
                             )

        message.save(using=self._db)

        return ticket


class Message(TimeStampedModel):
    """
    A single exchange between two users. A set of messages related to a specific ticket constitutes a conversation
    """

    conversation = models.ForeignKey(Conversation,
                                     blank=False,
                                     null=False,
                                     related_name='conversation',
                                     )

    body = models.TextField(max_length=message_model_settings.get('BODY_MAX_LENGTH'))

    is_read = models.BooleanField(blank=False,
                                  null=False,
                                  default=False)

    datetime_read = models.DateTimeField(blank=True,
                                         null=True,
                                         default=None)

    objects = MessageManager()

    @staticmethod
    def messages_received(user):
        return Message.objects.filter(conversation__receiver=user)

    @staticmethod
    def messages_sent(user):
        return Message.objects.filter(conversation__sender=user)


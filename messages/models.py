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

        # Whenever a new message is created, we need to make sure all messages in that conversation are visible.
        # For example, if two users exchange ten or fifteen messages and then one users "delete/hides" their
        # conversation, we need to unhide all of those messages so that the entirety of the conversation is visible
        # for both users when the receiver checks the new message.
        Message.mark_conversation_hidden_toggle(sender.id, receiver.id, ticket.id, False, True)

        receiver.send_mail(new_message_subject,
                           '',
                           html=render_to_string(new_message_template),
                           )


        message.save()

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

    # Has the RECEIVER of the message read it. This is a very obvious point but tripped me up.
    # Obviously we don't need to keep track of whether the sender has read the messaeg
    is_read = models.BooleanField(blank=False,
                                  null=False,
                                  default=False)

    datetime_read = models.DateTimeField(blank=True,
                                         null=True,
                                         default=None)

    # These fields are used when a user "deletes" a conversation from his inbox. We will effectively hide all of the
    # messages for that conversation for that user.
    is_hidden_from_sender = models.BooleanField(blank=False,
                                                null=False,
                                                default=False,
                                                )

    is_hidden_from_receiver = models.BooleanField(blank=False,
                                                  null=False,
                                                  default=False,
                                                  )

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
    def mark_conversation_read(current_user_id, ticket_id, other_user_id):
        """
        Find every message associated with a particular user/ticket id pair and mark all of them as read.
        Basically, indicate that a user has viewed a particular conversation with a
        particular user about a particular ticket.
        """
        if not current_user_id or not ticket_id or not other_user_id:
            return False

        # Obviously a user cannot have a conversation with themselves
        if current_user_id == other_user_id:
            return False

        unmarked_messages = Message.get_messages_received(current_user_id).filter(ticket_id=ticket_id)
        unmarked_messages.update(is_read=True)

        return True

    @staticmethod
    def mark_conversation_hidden_toggle(current_user_id, ticket_id, other_user_id, hide_toggle, both_users=False):
        """
        Find every message associated with a particular user/ticket id pair and toggle their hidden attribute
        Basically, if a user tries to delete a conversation, we will mark all messages as hidden for that particular
        user. If a new message is sent between those two users for that ticket, the hidden messages will then be
        unhidden. This function hides messages if they are visible and makes them visible them if they are hidden.

        I know that this is inefficient and we should probably have a "conversation" table to avoid marking
        messages every time a new message is sent, but we need to go live :(

        current_user_id = The user whose messages will be toggled, unless the both_users parameter is True.
        hide_toggle - This value will be true or false. True means hide the messages. False means make them visible.
        both_users = If this value is set to True, both messages for both users will be toggled.
                     This is used whenever a new message is sent in a conversation. We need to make sure no messages are
                     hidden.
        """

        if not current_user_id or not ticket_id or not other_user_id:
            return False

        # Obviously a user cannot have a conversation with themselves
        if current_user_id == other_user_id:
            return False

        # We actually need to grab all messages in the conversation, regardless of whether they are hidden or not.
        # This is because for any given message, we do not know if the user deleting is the sender or receiver.
        conversation_messages = Message.get_messages_in_conversation(current_user_id, other_user_id, ticket_id)

        # Are we toggling the messages for one user or both of them?
        if not both_users:
            # Figure out if the user that requested the delete is the sender or receiver and then mark the message as
            # hidden for that user.
            for message in conversation_messages:
                if message.sender.id == current_user_id:
                    message.is_hidden_from_sender = hide_toggle
                else:
                    message.is_hidden_from_receiver = hide_toggle
                    # If a user hides a conversation, we want to mark all messages that they received in that
                    # conversations as read, even if they aren't, to avoid having them contribute to the inbox total
                    # unread count in the navbar.
                    message.is_read = True
                message.save()
        else:
            conversation_messages.update(is_hidden_from_sender=hide_toggle)
            conversation_messages.update(is_hidden_from_receiver=hide_toggle)
            # If the messages are being hidden for both users, then mark all messages as read so that they don't
            # appear as unread in the inbox badge in the navbar.
            if hide_toggle:
                conversation_messages.update(is_read=True)

        return True

    @staticmethod
    def get_messages_received(user):
        """
        Returns a QuerySet of messages where the inputted user was the receiver
        """

        # Note that both users may function as both the sender and the receiver. After all, they will both send
        # and receive messages in a conversation (hopefully).
        return Message.objects.filter(receiver=user)

    @staticmethod
    def get_messages_sent(user):
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

    @staticmethod
    def last_message_time(user1, user2, ticket_id):
        """
        Returns the time between now and the time the last message was sent for a particular conversation
        """

        messages = Message.get_messages_in_conversation(user1, user2, ticket_id).order_by('-creation_timestamp')
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
    def get_all_messages_sorted(user):
        """
        FALSE: WHAT WE ORIGINALLY TRIED
        Returns a QuerySet of messages that are grouped according to the above definition of a conversation for a
        particular user.

        WHAT WE ACTUALLY Do
        READ ME:  We actually can't do the above.
        We could need to group by ticket, then other user, then creation_timestamp.
        But the thing is, we don't know who the other user is (is it the sender or reciever).
        We would need to maintain a concept of an inbox for each user, and then we would always know who the other user
        is.

        """

        return Message.all_messages(user).order_by('creation_timestamp')

    @staticmethod
    def message_count(user):
        """
        Get the total number of unread messages for a given user.
        """

        return Message.objects.filter(receiver=user.id).filter(is_read=False).count()


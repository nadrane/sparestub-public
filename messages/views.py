# Standard Imports
from collections import defaultdict, namedtuple

# Django Imports
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# SpareStub Imports
from .settings import send_message_form_settings
from .forms import SendMessageForm, MarkMessagesReadForm
from tickets.models import Ticket
from messages.models import Message
from utils.networking import ajax_http, non_field_errors_notification, form_success_notification
from registration.models import User


class MessageUserModal(TemplateView):
    template_name = 'messages/message_user_modal.html'

    def get_context_data(self, ticket_id, **kwargs):
        context = super(MessageUserModal, self).get_context_data(**kwargs)
        context['form_settings'] = send_message_form_settings

        # This should really never happen. We still just return a modal with missing ticket information if it does.
        try:
            ticket = Ticket.objects.get(pk=ticket_id)
        except ObjectDoesNotExist:
            pass

        context['ticket'] = ticket
        return context

@login_required()
def send_message(request):
    if request.method == 'POST':
        send_message_form = SendMessageForm(request.POST, request=request)
        if send_message_form.is_valid():

            sender = request.user
            ticket = send_message_form.cleaned_data.get('ticket')
            receiver = send_message_form.cleaned_data.get('receiver')
            body = send_message_form.cleaned_data.get('body')

            Message.objects.create_message(sender, receiver, ticket, body)
            return ajax_http(form_success_notification('Your message was sent successfully!'))
        else:
            return ajax_http(non_field_errors_notification(send_message_form))


@login_required
def inbox(request):
    message_tuple = namedtuple('message', ['pic_url', 'body', 'did_this_user_send', 'timestamp'])
    convo_header_tuple = namedtuple('convo_header', ['other_user_pic_url', 'name', 'age', 'absolute_url', 'location',
                                                     'rating'])
    ticket_ribbon_tuple = namedtuple('ticket_ribbon', ['ticket_id', 'absolute_url', 'price', 'when', 'where'])

    threads = defaultdict(defaultdict)   # Contains every conversation associated with a ticket/user id pair.
    messages = defaultdict(defaultdict)  # Contains every message associated with a ticket/user id pair
    convo_headers = defaultdict(defaultdict)  # The user information that appears above the actual conversation
                                              # in the inbox.
    ticket_ribbons = dict()    # The ribbon of ticket information that appears below the header and above the
                               # conversation.

    user = request.user

    if request.method == 'GET':
        our_user_profile_picture_url = user.get_profile_pic_url('search')  # The profile pic url of the user whose inbox
                                                                           # we are loading

        for index, message in enumerate(Message.get_all_messages_sorted(user)):
            ticket = message.ticket
            ticket_id = ticket.id

            # Check to see if the two messages from the same conversation
            sender = message.sender
            if user == sender:
                other_user = message.receiver
                did_this_user_send = True
                profile_picture = our_user_profile_picture_url
            else:
                other_user = sender
                did_this_user_send = False
                profile_picture = other_user.get_profile_pic_url('search')

            other_user_id = other_user.id
            name = other_user.get_full_name()
            body = message.body

            threads[ticket_id][other_user_id] = {'name': name,
                                                 'blurb': body,
                                                 'pic_url': profile_picture,
                                                 'last_timestamp': Message.last_message_time(user,
                                                                                             other_user,
                                                                                             ticket_id),
                                                 }

            if ticket_id not in ticket_ribbons:
                ticket_ribbons[ticket_id] = ticket_ribbon_tuple(ticket_id=ticket_id,
                                                                absolute_url=ticket.get_absolute_url(),
                                                                price=ticket.price,
                                                                when=ticket.start_datetime,
                                                                where=ticket.get_full_location(),
                                                                )

            if ticket_id in messages and other_user_id in messages[ticket_id]:
                messages[ticket_id][other_user_id].append(message_tuple(pic_url=profile_picture,
                                                                        body=body,
                                                                        did_this_user_send=did_this_user_send,
                                                                        timestamp=message.creation_timestamp,
                                                                        ))
            else:
                messages[ticket_id][other_user_id] = [message_tuple(pic_url=profile_picture,
                                                                    body=message.body,
                                                                    did_this_user_send=did_this_user_send,
                                                                    timestamp=message.creation_timestamp,
                                                                    )]

            if other_user_id not in convo_headers[ticket_id]:
                convo_headers[ticket_id][other_user_id] = convo_header_tuple(other_user_pic_url=profile_picture,
                                                                             name=name,
                                                                             age=other_user.age(),
                                                                             absolute_url=other_user.get_absolute_url(),
                                                                             location=ticket.location,
                                                                             rating=other_user.rating,
                                                                             )

        # The django template language cannot handle defaultdict's properly. This resolves our issue.
        # Django Issues explains why.
        messages.default_factory = None
        convo_headers.default_factory = None
        threads.default_factory = None
        for key in messages.keys():
            messages[key].default_factory = None
        for key in convo_headers.keys():
            convo_headers[key].default_factory = None
        for key in convo_headers:
            convo_headers[key].default_factory = None

        return render(request,
                      'messages/inbox.html',
                      {'threads': threads,
                       'messages': messages,
                       'convo_headers': convo_headers,
                       'ticket_ribbons': ticket_ribbons,
                       })

@login_required()
def mark_messages_read(request):
    """
    Mark all messages between two users for a particular ticket as read for the user that calls this url.
    """

    if request.method == 'POST':

        mark_message_read_form = MarkMessagesReadForm(request.POST)

        if mark_message_read_form.is_valid():

            user = request.user
            other_user_id = mark_message_read_form.cleaned_data.get('other_user_id')
            ticket_id = mark_message_read_form.cleaned_data.get('ticket_id')

            # make sure that the other user exists
            if not User.objects.filter(pk=other_user_id).exists():
                return ajax_http({'isSuccessful': False},
                                 status=400)

            # The user cannot have a conversation with himself
            if other_user_id == user.id:
                return ajax_http({'isSuccessful': False},
                                 status=400)

            if Message.mark_conversation_read(user.id, ticket_id, other_user_id):
                return ajax_http({'isSuccessful': True},
                                 status=200)

            else:
                return ajax_http({'isSuccessful': False},
                                 status=400,
                                 )

        return ajax_http({'isSuccessful': False},
                         status=400)
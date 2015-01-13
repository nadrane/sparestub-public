# Standard Imports
from collections import defaultdict, namedtuple

# Django Imports
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# SpareStub Imports
from tickets.models import Ticket
from messages.models import Message
from asks.models import Request
from utils.networking import ajax_http, non_field_errors_notification, form_success_notification

# Module Imports
from .settings import send_message_form_settings
from .forms import EditMessageForm, SendMessageForm


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
    import pdb
    pdb.set_trace()
    if request.method == 'POST':
        send_message_form = SendMessageForm(request.POST, request=request)
        if send_message_form.is_valid():

            sender = request.user
            ticket = send_message_form.cleaned_data.get('ticket')
            other_user = send_message_form.cleaned_data.get('other_user')
            body = send_message_form.cleaned_data.get('body')

            Message.objects.create_message(sender, other_user, ticket, body)
            return ajax_http(form_success_notification('Your message was sent successfully!'))
        else:
            return ajax_http(non_field_errors_notification(send_message_form))


@login_required
def inbox(request):
    message_tuple = namedtuple('message', ['pic_url', 'body', 'did_this_user_send', 'timestamp'])
    convo_header_tuple = namedtuple('convo_header', ['other_user_pic_url', 'name', 'age', 'absolute_url', 'location',
                                                     'rating', 'request_status', 'is_requester', 'request_expiration'])
    ticket_ribbon_tuple = namedtuple('ticket_ribbon', ['ticket_id', 'absolute_url', 'price', 'when', 'where'])
    thread_tuple = namedtuple('thread', ['name', 'ticket_title', 'pic_url', 'last_timestamp', 'request_status',
                                         'ticket_id', 'other_user_id'])

    threads = defaultdict(defaultdict)   # Contains every conversation associated with a ticket/user id pair.
    sorted_threads = list()              # A list of threads sorted by timestamp. What the template actually uses.
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
                # Has the user "deleted" this conversation from his inbox?
                if message.is_hidden_from_sender:
                    continue
                other_user = message.receiver
                did_this_user_send = True
                profile_picture = our_user_profile_picture_url
            else:
                # Has the user "deleted" this conversation from his inbox?
                if message.is_hidden_from_receiver:
                    continue
                other_user = sender
                did_this_user_send = False
                profile_picture = other_user.get_profile_pic_url('search')

            other_user_id = other_user.id
            name = other_user.get_full_name()
            body = message.body

            def get_request_information():
                """
                Grab a request record for this ticket/user combo if one exists
                First we need to determine who the requester would have been.
                Our inbox viewer might be a seller or a buyer, but the request can only be made by a buyer.
                """
                user_request, request_status, request_expiration = None, None, None
                if ticket.poster == user:
                    user_request = Request.get_last_request(other_user, ticket)
                     # The user viewing the inbox did not request this ticket. He is the seller.
                    is_requester = False if user_request else None
                elif ticket.poster == other_user:
                    user_request = Request.get_last_request(user, ticket)
                    # The user viewing the inbox did request this ticket. He is the buyer.
                    is_requester = True if user_request else None
                if user_request:
                    request_status = user_request.status
                    request_expiration = user_request.calculate_expiration_datetime()

                return request_status, is_requester, request_expiration

            if not (ticket_id in threads and other_user_id in threads[ticket_id]):
                request_status, is_requester, request_expiration = get_request_information()
                threads[ticket_id][other_user_id] = thread_tuple(name=name,
                                                                 ticket_title=ticket.title,
                                                                 pic_url=profile_picture,
                                                                 last_timestamp=Message.last_message_time(user,
                                                                                                          other_user,
                                                                                                          ticket_id),
                                                                 request_status=request_status,
                                                                 ticket_id=ticket_id,
                                                                 other_user_id=other_user_id,
                                                                 )

            if ticket_id not in ticket_ribbons:
                ticket_ribbons[ticket_id] = ticket_ribbon_tuple(ticket_id=ticket_id,
                                                                absolute_url=ticket.get_absolute_url(),
                                                                price=ticket.price,
                                                                when=ticket.get_formatted_start_datetime(),
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
                if not request_status or not is_requester:
                    request_status, is_requester, request_expiration = get_request_information()
                convo_headers[ticket_id][other_user_id] = \
                    convo_header_tuple(other_user_pic_url=profile_picture,
                                       name=name,
                                       age=other_user.age(),
                                       absolute_url=other_user.get_absolute_url(),
                                       location=ticket.location,
                                       rating=other_user.rating,
                                       request_status=request_status,
                                       is_requester=is_requester,
                                       request_expiration=request_expiration,
                                       )

        # The django template language cannot handle defaultdict's properly. This resolves our issue.
        # Django Issues explains why.
        messages.default_factory = None
        convo_headers.default_factory = None
        for key in messages.keys():
            messages[key].default_factory = None
        for key in convo_headers.keys():
            convo_headers[key].default_factory = None
        for key in convo_headers:
            convo_headers[key].default_factory = None

        for ticket_id in threads:
            for other_user_id in threads[ticket_id]:
                sorted_threads.append(threads[ticket_id][other_user_id])
        sorted_threads.sort(key=lambda x: x.last_timestamp, reverse=True)

        return render(request,
                      'messages/inbox.html',
                      {'threads': sorted_threads,
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
        mark_message_read_form = EditMessageForm(request.POST, request=request)

        if mark_message_read_form.is_valid():
            sender_id = request.user.id
            other_user_id = mark_message_read_form.cleaned_data.get('other_user_id')
            ticket_id = mark_message_read_form.cleaned_data.get('ticket_id')

            if Message.mark_conversation_read(sender_id, ticket_id, other_user_id):
                return ajax_http({'isSuccessful': True},
                                 status=200)

            else:
                return ajax_http({'isSuccessful': False},
                                 status=400,
                                 )

        return ajax_http({'isSuccessful': False},
                         status=400)

@login_required()
def messages_hidden_toggle(request):
    """
    Mark all messages between two users for a particular ticket as read for the user that calls this url.
    """

    if request.method == 'POST':
        toggle_message_form = EditMessageForm(request.POST, request=request)

        if toggle_message_form.is_valid():
            sender_id = request.user.id
            other_user_id = toggle_message_form.cleaned_data.get('other_user_id')
            ticket_id = toggle_message_form.cleaned_data.get('ticket_id')

            if Message.mark_conversation_hidden_toggle(sender_id, ticket_id, other_user_id, True):
                return ajax_http({'isSuccessful': True},
                                 status=200)
            else:
                return ajax_http({'isSuccessful': False},
                                 status=400,
                                 )

        return ajax_http({'isSuccessful': False},
                         status=400)
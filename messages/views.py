# Standard Imports
from collections import defaultdict, namedtuple

# Django Imports
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.decorators import login_required

# SpareStub Imports
from .settings import send_message_form_settings
from .forms import SendMessageForm
from tickets.models import Ticket
from messages.models import Message
from utils.networking import ajax_http, non_field_errors_notification, form_success_notification
from photos.models import Photo


def message_user_modal(request, ticket_id):

    # Ticket does not exist.
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise Http404()

    if request.method == 'GET':
        return render(request,
                      'messages/message_user_modal.html',
                      {'form_settings': send_message_form_settings,
                       'ticket': ticket,
                       })

@login_required()
def send_message(request, ticket_id):
    if request.method == 'POST':
        sender = request.user

        ticket = Ticket.objects.get(pk=ticket_id)

        if ticket:
            receiver = ticket.poster
        else:
            return ajax_http({'isSuccessful': False,
                              'notification_type': 'alert-danger',
                              'notification_content': 'This ticket does not exist!'
                              })

        # Make sure that the username entered is the actual poster of this ticket
        if sender == receiver:
            return ajax_http({'isSuccessful': False,
                              'notification_type': 'alert-danger',
                              'notification_content': "You can't send a message to yourself, silly!"
                              })

        if not ticket.is_active:
            return ajax_http({'isSuccessful': False,
                              'notification_type': 'alert-danger',
                              'notification_content': 'The poster of this ticket cancelled it in the last few minutes!'
                              })

        send_message_form = SendMessageForm(request.POST)
        if send_message_form.is_valid():
            body = request.POST.get('body')
            Message.objects.create_message(sender, receiver, ticket, body)
            return ajax_http(form_success_notification('Your message was sent successfully!'))
        else:
            return ajax_http(non_field_errors_notification(send_message_form))


@login_required
def inbox(request):
    message = namedtuple('message', 'other_user_pic_url', 'body', 'did_this_user_send')
    convo_header = namedtuple('convo_header', 'pic_url', 'name', 'place', 'rating')
    ticket_ribbon = namedtuple('ticket_ribbon', 'ticket_id', 'price', 'when', 'where')

    conversations = dict()  # The threads with difference users about different tickets that appear on the
                            # left side of the inbox screen.
    messages = defaultdict(defaultdict)  # Contains every message associated with a ticket_user_id pair
    convo_headers = defaultdict(list)    # The user information that appears above the actual conversation in the inbox.
    ticket_ribbons = defaultdict(list)   # The ribbon of ticket information that appears below the header and above the
                                         # conversation.

    user = request.user

    if request.method == 'GET':

        last_ticket_id = ''
        for index, message in enumerate(Message.get_all_messages_sorted(user)):
            ticket_id = message.ticket.id
            # Check to see if the two messages from the same conversation
            if ticket_id != last_ticket_id:
                sender = message.sender
                if user == sender:
                    other_user = message.receiver
                    did_this_user_send = True
                else:
                    other_user = sender

                name = other_user.get_full_name()
                try:
                    profile_picture = other_user.profile_picture
                # Some users don't have profile pictures. This is okay. We will use a default in the template.
                except Photo.DoesNotExist:
                    profile_picture = ''

                if profile_picture:
                    profile_picture = profile_picture.search_thumbnail.url

                blurb = message.body

                last_timestamp = message.creation_timestamp
                conversations[ticket_id] = {'name': name,
                                            'blurb': blurb,
                                            'pic_url': profile_picture,
                                            'last_timestamp': last_timestamp,
                                            }


            last_ticket_id = ticket_id

            if ticket_id in messages and other_user.id in messages[ticket_id]:
                messages[ticket_id][other_user.id].append(message(other_user_pic_url=profile_picture,
                                                                  body=message.body,
                                                                  did_this_user_send=did_this_user_send,
                                                                  ))
            else:
                messages[ticket_id][other_user.id] = [message.body]

            if ticket_id in convo_headers and other_user.id in convo_headers[ticket_id]:
                convo_headers[ticket_id][other_user.id].append(convo_header(other_user_pic_url=profile_picture,
                                                                            body=message.body,
                                                                            did_this_user_send=did_this_user_send,
                                                                            ))

        if conversations:
            try:
                current_user_pic_url = user.profile_picture
            # Some users don't have profile pictures. This is okay. We will use a default in the template.
            except Photo.DoesNotExist:
                profile_picture = ''

            if current_user_pic_url:
                current_user_pic_url = profile_picture.search_thumbnail.url

        # The django template language cannot handle defaultdict's properly. This resolves our issue.
        # SO explains why.
        messages.default_factory = None
        for key in messages.keys():
            messages[key].default_factory = None

        return render(request,
                      'messages/inbox.html',
                      {'conversations': conversations,
                       'messages': messages,
                       'convo_headers': convo_headers,
                       'ticket_ribbons': ticket_ribbons,
                       })
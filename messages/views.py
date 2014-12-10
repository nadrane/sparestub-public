# Standard Imports
from collections import defaultdict

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

@login_required
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
    user = request.user
    if request.method == 'GET':
        conversations = dict()   # All messages that the user has sent or been sent
        last_ticket_id = ''
        for message in Message.get_all_messages_sorted(user):
            ticket_id = message.ticket.id
            # Check to see if the two messages from the same conversation
            if ticket_id != last_ticket_id:
                sender = message.sender
                if user == sender:
                    other_user = message.receiver
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

        import pdb
        pdb.set_trace()
        first_ticket = conversations[conversations.values()]

        return render(request,
                      'messages/inbox.html',
                      {'conversations': conversations,
                      })
# Django Imports
from django.shortcuts import render
from django.http import Http404

# SpareStub Imports
from .settings import send_message_form_settings
from .forms import SendMessageForm
from tickets.models import Ticket
from messages.models import Message
from utils.networking import ajax_http, non_field_errors_notification, form_success_notification


def message_user_modal(request, ticket_id):
    ticket = Ticket.objects.get(pk=ticket_id)

    if not ticket:
        raise Http404('Ticket {} does not exist'.format(ticket_id))

    if request.method == 'GET':
        return render(request,
                      'messages/message_user_modal.html',
                      {'form_settings': send_message_form_settings,
                       'ticket': ticket,
                       })


def send_message(request, ticket_id):
    import pdb
    pdb.set_trace()

    if request.method == 'POST':
        sender = request.user

        if sender.is_anonymous():
            return ajax_http({'isSuccessful': False,
                              'notification_type': 'alert-danger',
                              'notification_content': 'You need to be logged in to send a message!'
                              })

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


def inbox(request):
    pass
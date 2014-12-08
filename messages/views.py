# Django Imports
from django.shortcuts import render
from django.http import Http404

# SpareStub Imports
from .settings import send_message_form_settings
from .forms import SendMessageForm
from tickets.models import Ticket
from messages.models import Message, Conversation

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
            raise Http404('You need to be logged in to send a message!')

        ticket = Ticket.objects.get(pk=ticket_id)

        if ticket:
            receiver = ticket.poster
        else:
            raise Http404('Ticket {} does not exist'.format(ticket_id))

        # Make sure that the username entered is the actual poster of this ticket
        if sender == receiver:
            raise Http404('You cannot send a message to yourself!')

        if not ticket.is_active:
            raise Http404('This ticket is no longer active!')

        send_message_form = SendMessageForm(request.POST)
        if send_message_form.is_valid():
            body = request.POST.get('body')
            message = Message.objects.create_message(sender, receiver, ticket, body)


def inbox(request):
    pass
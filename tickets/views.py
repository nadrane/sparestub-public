# Django imports
from django.contrib.auth.decorators import login_required
from .settings import ticket_submit_form_settings
from django.shortcuts import render

@login_required()
def submit_ticket(request):
    # If the form has been submitted by the user
    if request.method == 'POST':
        pass

    return render(request,
                  'tickets/submit_ticket.html',
                  {'form_settings': ticket_submit_form_settings}
                  )
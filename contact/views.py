# -*- coding: utf-8 -*-
import requests

import sendgrid
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse

from .forms import ContactForm
from .settings import contact_form_settings
import pdb

from django.template import RequestContext

def submit(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject_type = contact_form.cleaned_data.get('subject_type', 'empty subject')
            body = contact_form.cleaned_data.get('body', 'empty body')
            from_email_address = contact_form.cleaned_data.get('from_email_address', "nick@sparestub.com")
            sg = sendgrid.SendGridClient('SpareStub', 'rrY8qQVYwMsAV=Z^nTC4X')
            message = sendgrid.Mail()
            message.add_to('feedback@sparestub.com')
            message.set_subject(subject_type)
            message.set_html(body)
            message.set_from(from_email_address)
            status, msg = sg.send(message)

        #TODO it might be nice to just close to popup modal and submit the email using an ajax request later
        return redirect("contact.views.home")

    else:
        contact_form = ContactForm()

    return render(request,
                  'contact/contact_form.html',
                  {'contact_form': contact_form,
                   'form_settings': contact_form_settings,
                   }
                  )


def home(request):
    return render(request,
                  'home.html'
                  )
"""
          <div class="inner cover">
            <h1 class="cover-heading" style="text-align: center">Imagine this:</h1>
            <p class="lead" style="text-align: center">Joey purchased two tickets to an event, but his friend bails and he has no one to go with.<br> Poor Joey!</p>
            <p class="lead" style="text-align: center">Across town, Susie wants to go to the event, but has no ticket and no one to go with. Poor Susie!</p>
            <p class="lead" style="text-align: center"><b>Introducing SpareStub!</b> We will help connect Joey and Susie. After reviewing each other’s profiles and messaging a bit, Susie will not only buy Joey's extra ticket but also accompany him to the event.</p>
            <h2 class="cover-heading" style="text-align: center"><i>Convenient. Social. SpareStub.</i><br> Coming: Spring 2015</h2>
            <p class="lead" style="font-size: 100%" style="text-align: center">As we develop SpareStub, we would love ideas, feedback and Beta users! If you would like periodic updates on SpareStub development and release, or would like to be included in helping to design and test the product, click below to send us an email! </p>
        </div>

            <p class="lead" style="text-align: center">

            <a href=mailto:feedback@sparestub.com class="btn btn-lg btn-default">I'm in!</a>


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
  </body>

</html>
    	"""
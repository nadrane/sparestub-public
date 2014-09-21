# -*- coding: utf-8 -*-
import requests

import sendgrid
from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting


def contact(request):
    if request.method == 'POST':
        email = request.get('from_email_address', '')
        im_in = request.get('subject_type', '')
        body = request.get('body', '')
        print email
        print im_in
        print body
        if all(email, im_in, body):
            sg = sendgrid.SendGridClient('SpareStub', 'rrY8qQVYwMsAV=Z^nTC4X')
            message = sendgrid.Mail()
            message.add_to('feedback@sparestub.com')
            message.set_subject(im_in)
            message.set_html(body)
            message.set_from(email)
            status, msg = sg.send(message)

#or


def index(request):
    return HttpResponse("""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>SpareStub</title>

    <!-- Bootstrap core CSS -->
    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css" rel="stylesheet">

    <!-- Homepage CSS -->
    <link href="https://s3.amazonaws.com/sparestub/static/homepage2.css" rel="stylesheet">
  </head>

  <body>

    <div class="site-wrapper">

      <div class="site-wrapper-inner">

        <div class="cover-container">

          <div class="masthead clearfix">
            <div class="inner">
            </div>
          </div>

          <div class="inner cover">
            <h1 class="cover-heading" style="text-align: center">Imagine this:</h1>
            <p class="lead" style="text-align: center">Joey purchased two tickets to an event, but his friend bails and he has no one to go with.<br> Poor Joey!</p>
            <p class="lead" style="text-align: center">Across town, Susie wants to go to the event, but has no ticket and no one to go with. Poor Susie!</p>
            <p class="lead" style="text-align: center"><b>Introducing SpareStub!</b> We will help connect Joey and Susie. After reviewing each other’s profiles and messaging a bit, Susie will not only buy Joey's extra ticket but also accompany him to the event.</p>
            <h2 class="cover-heading" style="text-align: center"><i>Convenient. Social. SpareStub.</i><br> Coming: Spring 2015</h2>
            <p class="lead" style="font-size: 100%" style="text-align: center">As we develop SpareStub, we would love ideas, feedback and Beta users! If you would like periodic updates on SpareStub development and release, or would like to be included in helping to design and test the product, click below to send us an email! </p>
            

            <p class="lead" style="text-align: center">

            <button class="btn btn-lg btn-default" data-toggle="modal" data-target="#modal-contact-form">I'm in!</button>

          </div>

        </div>

      </div>

    </div>

    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
    <script src="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
  </body>

  <div class="modal fade" id="modal-contact-form" tabindex="-1" role="dialog" aria-labelledby="Contact form" aria-hidden="true">
    <div class="modal-dialog modal-sm">
      <div class="modal-content" id="modal-contact-form-content">
          <div class="modal-header">
            <h4 class="modal-title">Email Us</h4>
          </div>

          <div class="modal-body">
            <form id="contact-form" class="form-horizontal">

              <div class="form-group">
                <label for="contact-email" class="control-label sr-only"></label>
                <input id="contact-email" class="form-control" type="email" required name="from_email_address"
                       placeholder="Email Address">
              </div>

              <div class="form-group">
                <label for="contact-subject-type" class="control-label sr-only"></label>
                <select id="contact-subject-type" class="form-control" name="subject_type" required>
                  <option value="" disabled selected>I'm in for...</option>]
                    <option value="str">Beta only</option>
                    <option value="str">Updates only</option>
                    <option value="str">Beta and updates</option>
                </select>
              </div>  <!-- form group -->

              <div class="form-group">
                <label for="contact-body" class="control-label sr-only"></label>
                <textarea id="contact-body" class="form-control" name="body" required placeholder="Your message here"></textarea>
              </div>  <!-- form group -->
            </form>  <!-- contact form -->
          </div>  <!-- modal body -->
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
            <button id="contact-form-button" class="btn btn-primary form-submit-button" form="contact-form" type="submit">Submit</button>
          </div>
      </div>
    </div>
  </div>


<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-55020709-1', 'auto');
  ga('send', 'pageview');

</script>

</html>
    	""")
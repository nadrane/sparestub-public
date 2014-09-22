# -*- coding: utf-8 -*-
import requests

import sendgrid
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Greeting


def contact(request):
    import pdb
    pdb.set_trace()
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

    return redirect('/')

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

            <a href=mailto:feeback@sparestub.com class="btn btn-lg btn-default">I'm in!</a>

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
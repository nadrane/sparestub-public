# -*- coding: utf-8 -*-
import requests

from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

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
    <title>Cover Template for Bootstrap</title>

    <!-- Bootstrap core CSS -->
    <link href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css" rel="stylesheet">

    <!-- Homepage CSS -->
    <link href="https://s3.amazonaws.com/sparestub/static/homepage.css" rel="stylesheet">
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
            <p class="lead" style="text-align: center"><a href="mailto:feedback@sparestub.com" class="btn btn-lg btn-default">I'm in!</a></p>
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
</html>
    	""")
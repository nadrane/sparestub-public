import requests

from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting

def index(request):
    return HttpResponse("""
    	<html>
    	<head>
    	<title>SpareStub</title>
    	</head>
    	Welcome to sparestub
    	</html>
    	""")

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, 'db.html', {'greetings': greetings})


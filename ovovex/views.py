from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    """
    Home page view
    """
    context = {
        'title': 'Welcome to Ovovex',
        'description': 'Your next-generation platform for innovative solutions.',
    }
    return render(request, 'home.html', context)

def health_check(request):
    """
    Simple health check endpoint
    """
    return HttpResponse("OK", content_type="text/plain")
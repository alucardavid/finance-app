from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
import requests


def index(request):
    """The home page for Finance App"""
    url = "http://127.0.0.1:8001/balances/"
    response = requests.get(url)
    data = response.json()
    
    context = {'balances': data}

    return render(request, 'finance/index.html', context)


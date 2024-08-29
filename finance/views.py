from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from . import api   
import requests


def index(request):
    """The home page for Finance App"""
    context = api.get_all_balances()
        
    return render(request, 'finance/index.html', context)


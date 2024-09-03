from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from . import api   
import requests


def index(request):
    """The home page for Finance App"""
        
    return render(request, 'finance/index.html')

def balances(request):
    """Page to show all balances"""
    context = api.get_all_balances()
        
    return render(request, 'finance/balances/balances.html', context)

def balance(request, balance_id):
    """Show balance by id"""

    context = api.get_balance_by_id(balance_id)

    return render(request, 'finance/balances/balance.html', context)

def new_balance(request):
    """Create a new balance"""
    if request.method != "POST":
        return render(request, 'finance/balances/new_balance.html')
    else:
        data = request.POST.get("amount", "")
        return HttpResponse(data)

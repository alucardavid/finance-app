from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from . import api   
from .forms import BalanceForm
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
        form = BalanceForm()
    else:
        post = request.POST.copy()
        post['value'] = post['value'].replace('.', '').replace(',', '.')
        form = BalanceForm(data=post)
        if form.is_valid():
            new_balance = form.save(commit=False)
            db_new_balance = api.create_balance(new_balance.description, new_balance.value, new_balance.show)
            return redirect('finance:balances')
        

    context = {'form': form}
    return render(request, 'finance/balances/new_balance.html', context)




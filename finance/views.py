from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.formats import localize
from . import api   
from .forms import BalanceForm, VariableExpenseForm
import requests
import sys, datetime




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

def variable_expenses(request):
    """Show all variable expenses"""
    
    context = api.get_all_variable_expenses()

    return render(request, 'finance/variable_expenses/variable_expenses.html', context)

def new_variable_expense(request):
    """Create a new variable expense"""
    if request.method != "POST":
        form = VariableExpenseForm()
    else:
        post = request.POST.copy()
        post['amount'] = post['amount'].replace('.', '').replace(',', '.')
        form = VariableExpenseForm(data=post)
        if form.is_valid():
            new_variable_expense = form.save(commit=False)
            db_new_variable_expense = api.create_variable_expense(new_variable_expense)
            return redirect('finance:variable_expenses')

    context = {'form': form}
    return render(request, 'finance/variable_expenses/new_variable_expense.html', context)

def edit_variable_expense(request, variable_expense_id):
    """Edit a variable expense"""
    if request.method != "POST":
        variable_expense = api.get_variable_expense_by_id(variable_expense_id)["variable_expense"]
        variable_expense["date"] = datetime.datetime.strptime(variable_expense["date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        variable_expense["form_of_payment"] = variable_expense["form_of_payments"]["id"]
        form = VariableExpenseForm(data=variable_expense)
    else:
        post = request.POST.copy()
        post['amount'] = post['amount'].replace('.', '').replace(',', '.')
        form = VariableExpenseForm(data=post)
        if form.is_valid():
            new_variable_expense = form.save(commit=False)
            db_new_variable_expense = api.create_variable_expense(new_variable_expense)
            return redirect('finance:variable_expenses')

    context = {'form': form}
    return render(request, 'finance/variable_expenses/edit_variable_expense.html', context)



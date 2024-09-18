from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.formats import localize
from . import api   
from .forms import BalanceForm, VariableExpenseForm, MonthlyExpenseForm
import requests
import sys, datetime

def index(request):
    """The home page for Finance App"""
        
    return render(request, 'finance/index.html')

def balances(request):
    """Page to show all balances"""
    context = api.get_all_balances()
        
    return render(request, 'finance/balances/balances.html', context)

def edit_balance(request, balance_id):
    """Edit a balance """
    if request.method != "POST":
        balance = api.get_balance_by_id(balance_id)["balance"]
        form = BalanceForm(data=balance)
    else:
        post = request.POST.copy()
        post['value'] = post['value'].replace('.', '').replace(',', '.')
        form = BalanceForm(data=post)
        if form.is_valid():
            new_balance = form.save(commit=False)
            db_new_balance = api.update_balance(new_balance, balance_id)
            return redirect('finance:balances')

    context = {'form': form, 'balance': balance}

    return render(request, 'finance/balances/edit_balance.html', context)

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
            db_new_variable_expense = api.update_variable_expense(new_variable_expense, variable_expense_id)
            return redirect('finance:variable_expenses')

    context = {'form': form, 'expense': variable_expense}
    return render(request, 'finance/variable_expenses/edit_variable_expense.html', context)

def monthly_expenses(request):
    """Get all monthly expenses"""
    page = int(request.GET.get('page') if request.GET.get('page') is not None else 1)
    limit = int(request.GET.get('limit') if request.GET.get('limit') is not None else 10)
    pages = []
    monthly_expenses = api.get_all_monthly_expenses(page, limit)

    for i in range(1 if page <=5 else page - 4, 6 if page <= 5 else (page + 1)):
        pages.append(i)

    context = { 
        'monthly_expenses': monthly_expenses,
        'page': page,
        'pages': pages,
        'prev_page': page - 1,
        'next_page': page + 1,
        'last_page': monthly_expenses["total_pages"],
        'showing': f"{(page * limit) - (limit - 1)} a {page * limit} de {format(monthly_expenses["count"], ',d').replace(",", ".")}"
    }
    return render(request, 'finance/monthly_expenses/monthly_expenses.html', context)

def new_monthly_expense(request):
    """Create a new monthly expense"""
    if request.method != "POST":
        form = MonthlyExpenseForm()

    context = {'form': form}
    return render(request, 'finance/monthly_expenses/new_monthly_expense.html', context)
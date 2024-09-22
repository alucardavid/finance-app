from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.formats import localize
from django import forms
from .forms import BalanceForm, VariableExpenseForm, MonthlyExpenseForm
from .models import MonthlyExpense
import sys, datetime, csv, requests
from . import api
from datetime import date, datetime


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
    due_date = request.GET.get('due_date')
    order_by = "monthly_expenses.id desc" if due_date is None else "monthly_expenses.form_of_payment_id, monthly_expenses.place, monthly_expenses.description asc"
    where = request.GET.get('where')
    monthly_expenses = api.get_all_monthly_expenses(page, limit, order_by, due_date, where)
    last_page = monthly_expenses["total_pages"]
    total_items = monthly_expenses["count"]
    pages = []

    if last_page <= 5:
        for i in range(1, last_page+1):
            pages.append(i)
    else:
        for i in range(1 if page <=5 else page - 4, 6 if page <= 5 else (page + 1)):
            pages.append(i)

    context = { 
        'monthly_expenses': monthly_expenses,
        'page': page,
        'pages': pages,
        'prev_page': page - 1,
        'next_page': page + 1,
        'last_page': last_page,
        'showing': f"{(page * limit) - (limit - 1)} a {(page * limit) if (page * limit) <= total_items else total_items } de {format(monthly_expenses["count"], ',d').replace(",", ".")}",
        'due_date': due_date,
        'where': where
    }
    return render(request, 'finance/monthly_expenses/monthly_expenses.html', context)

def new_monthly_expense(request):
    """Create a new monthly expense"""
    if request.method != "POST":
        form = MonthlyExpenseForm()
    else:
        post = request.POST.copy()
        post['amount'] = post['amount'].replace('.', '').replace(',', '.')
        form = MonthlyExpenseForm(data=post)
        if form.is_valid():
            new_monthly_expense = form.save(commit=False)
            db_new_monthly_expense = api.create_monthly_expense(new_monthly_expense)
            return redirect('finance:monthly_expenses')

    
    context = {'form': form}
    return render(request, 'finance/monthly_expenses/new_monthly_expense.html', context)

def edit_monthly_expense(request, monthly_expense_id):
    """Edit a monthly expense"""
    if request.method != "POST":
        expense = api.get_monthly_expense_by_id(monthly_expense_id)["monthly_expense"]
        expense["date"] = datetime.datetime.strptime(expense["date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        expense["due_date"] = datetime.datetime.strptime(expense["due_date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        expense["form_of_payment"] = expense["form_of_payments"]["id"]
        form = MonthlyExpenseForm(data=expense)
    else:
        post = request.POST.copy()
        post['amount'] = post['amount'].replace('.', '').replace(',', '.')
        form = MonthlyExpenseForm(data=post)
        if form.is_valid():
            new_monthly_expense = form.save(commit=False)
            db_new_monthly_expense = api.update_monthly_expense(new_monthly_expense, monthly_expense_id)
            return redirect('finance:monthly_expenses')

    context = {'form': form, 'expense': expense}
    return render(request, 'finance/monthly_expenses/edit_monthly_expense.html', context)

def import_monthly_expenses(request):
    """Import expenses from csv file"""
    file_data = request.FILES['file'].read().decode('utf-8')
    expenses_imported = []
    
    lines = file_data.split('\n')
    
    try:
        for index, line in enumerate(lines):
            if index > 0:
                line = line.split(',')
                print(line, file=sys.stderr)
                expense =  MonthlyExpense(
                    date = datetime.strptime(line[0], '%Y-%m-%d').date(),
                    place = line[1],
                    description = line[2],
                    amount = line[3],
                    total_plots = line[4],
                    current_plot = line[5],
                    due_date = datetime.strptime(line[6], '%Y-%m-%d').date(),
                    form_of_payment_id = line[7].replace('\r', '')
                )

                # expenses_imported.append(api.create_monthly_expense(expense))

    except:
        return HttpResponse("Wasn't possible to import expenses.")
        
    return HttpResponse("Expenses was imported with success.")



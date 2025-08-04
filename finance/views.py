from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.formats import localize
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from finance import open_finance_api
from .forms import BalanceForm, VariableExpenseForm, MonthlyExpenseForm, IncomingForm, ExpenseCategoryForm
from .models import MonthlyExpense
import sys, datetime, csv, requests
from . import api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tabula import read_pdf
import os
from setup.settings import BASE_DIR
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger('finance')

@login_required
def index(request):
    """The home page for Finance App"""
    balances = api.get_all_balances()["balances"]
    total_monthly_expenses_pend = _get_monthly_expense_pend(request)
    expenses_next_month = api.get_all_monthly_expenses(page=1, limit=999, due_date=(datetime.today()+relativedelta(months=1)).strftime("%Y-%m"), where="Pendente")["items"]
    pending_incomings = api.get_all_incomings(1, 999,'Pendente')["items"]

    total_balances = round(sum(balance["value"] for balance in balances))
    total_expenses_next_month = round(sum(expense["amount"] for expense in expenses_next_month))
    total_incomings = round(sum(incoming["amount"] for incoming in pending_incomings))

    context = {
        'total_balances': total_balances,
        'total_monthly_expenses_pend': total_monthly_expenses_pend,
        'total_expenses_next_month': total_expenses_next_month,
        'total_balances_min_expenses': total_balances - total_monthly_expenses_pend,
        'total_incomings': total_incomings,
        'balance_plus_incomings': total_balances + total_incomings,
        'balance_incomings_pend': total_balances + total_incomings - total_monthly_expenses_pend,
    }


    return render(request, 'finance/index.html', context)

@login_required
def balances(request):
    """Page to show all balances"""
    context = api.get_all_balances()
        
    return render(request, 'finance/balances/balances.html', context)

@login_required
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

@login_required
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

@login_required
def sync_balances(request):
    """Sync balances with external API"""
    balances = api.get_all_balances()["balances"]
    for balance in balances:
        if not balance["id_connector"] or not balance["id_account_bank"]:
            continue
        
        bank_account = open_finance_api.retrieve_account(balance["id_connector"], balance["id_account_bank"])
        if "error" in bank_account:
            logger.error(f"Error retrieving account {balance['description']}: {bank_account['error']}")
            messages.error(request, f"Error retrieving account {balance['description']}: {bank_account['error']}")
            continue
        
        balance["value"] = bank_account["balance"]
        balance["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        updated_balance = api.update_balance(balance, balance["id"])
        if "error" in updated_balance:
            logger.error(f"Error updating balance {balance['id']}: {updated_balance['error']}")


    return redirect('finance:balances')

@login_required
def variable_expenses(request):
    """Show all variable expenses"""
    page = int(request.GET.get('page') if request.GET.get('page') is not None else 1)
    limit = int(request.GET.get('limit') if request.GET.get('limit') is not None else 10)
    order_by = "variable_expenses.id desc"
    where = request.GET.get('where')
    variable_expenses = api.get_all_variable_expenses(page, limit, order_by, where)
    last_page = variable_expenses["total_pages"]
    total_items = variable_expenses["count"]
    pages = []

    if last_page <= 5:
        for i in range(1, last_page+1):
            pages.append(i)
    else:
        for i in range(1 if page <=5 else page - 4, 6 if page <= 5 else (page + 1)):
            pages.append(i)

    context = { 
        'variable_expenses': variable_expenses,
        'page': page,
        'pages': pages,
        'prev_page': page - 1,
        'next_page': page + 1,
        'last_page': last_page,
        'showing': f"{(page * limit) - (limit - 1)} a {(page * limit) if (page * limit) <= total_items else total_items } de {format(variable_expenses['count'], ',d').replace(',', '.')}",
        'where': where
    }

    return render(request, 'finance/variable_expenses/variable_expenses.html', context)

@login_required
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

@login_required
def edit_variable_expense(request, variable_expense_id):
    """Edit a variable expense"""
    if request.method != "POST":
        variable_expense = api.get_variable_expense_by_id(variable_expense_id)["variable_expense"]
        variable_expense["date"] = datetime.strptime(variable_expense["date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
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

@login_required
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
        'showing': f"{(page * limit) - (limit - 1)} a {(page * limit) if (page * limit) <= total_items else total_items } de {format(monthly_expenses['count'], ',d').replace(',', '.')}",
        'due_date': due_date,
        'where': where
    }
    return render(request, 'finance/monthly_expenses/monthly_expenses.html', context)

@login_required
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

@login_required
def edit_monthly_expense(request, monthly_expense_id):
    """Edit a monthly expense"""
    if request.method != "POST":
        expense = api.get_monthly_expense_by_id(monthly_expense_id)["monthly_expense"]
        expense["date"] = datetime.strptime(expense["date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        expense["due_date"] = datetime.strptime(expense["due_date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        expense["form_of_payment"] = expense["form_of_payments"]["id"]
        expense["expense_category"] = expense["expense_categorys"]["id"]
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

@login_required
def import_monthly_expenses(request):
    """Import expenses from csv file"""
    file_data = request.FILES['file'].read().decode('utf-8')
    expenses_imported = []
    
    lines = file_data.split('\n')
    
    try:
        for index, line in enumerate(lines):
            line = line.split(';')
            
            if len(line) > 0:
                expense =  MonthlyExpense(
                    date = datetime.strptime(line[0], '%Y-%m-%d').date(),
                    place = line[1],
                    description = line[2],
                    amount = line[3],
                    total_plots = line[4],
                    current_plot = line[5],
                    due_date = datetime.strptime(line[6], '%Y-%m-%d').date(),
                    form_of_payment_id = line[7],
                    expense_category_id = line[8].replace('\r', '')
                )
                
                expenses_imported.append(api.create_monthly_expense(expense))

    except:
        return HttpResponseBadRequest("Wasn't possible to import expenses.")
        
    return HttpResponse("Expenses was imported with success.")

@login_required
def incomings(request):
    """Page to show all incomings"""
    page = int(request.GET.get('page') if request.GET.get('page') is not None else 1)
    limit = int(request.GET.get('limit') if request.GET.get('limit') is not None else 10)
    where = request.GET.get('where')
    incomings = api.get_all_incomings(page, limit, None, "id desc", where)
    last_page = incomings["total_pages"]
    total_items = incomings["count"]
    pages = []

    if last_page <= 5:
        for i in range(1, last_page+1):
            pages.append(i)
    else:
        for i in range(1 if page <=5 else page - 4, 6 if page <= 5 else (page + 1)):
            pages.append(i)
    
    print(incomings["limit"])

    context = { 
        'incomings': incomings,
        'page': page,
        'pages': pages,
        'prev_page': page - 1,
        'next_page': page + 1,
        'last_page': last_page,
        'showing': f"{(page * limit) - (limit - 1)} a {(page * limit) if (page * limit) <= total_items else total_items } de {format(incomings['count'], ',d').replace(',', '.')}",
        'where': where
    }

    return render(request, 'finance/incomings/incomings.html', context)

@login_required
def new_incoming(request):
    """Page to add new incoming"""
    if request.method != "POST":
        form = IncomingForm()
    else:
        post = request.POST.copy()
        post["amount"] = post["amount"].replace('.', '').replace(',', '.')
        form = IncomingForm(data=post)
        if form.is_valid():
            new_incoming = form.save(commit=False)
            db_new_incoming = api.create_incoming(new_incoming)
            return redirect('finance:incomings')
    

    context = { "form": form}

    return render(request, 'finance/incomings/new_incoming.html', context)

@login_required
def edit_incoming(request, incoming_id):
    """Page to edit a incoming"""
    if request.method != "POST":
        incoming = api.get_incoming_by_id(incoming_id)["incoming"]
        incoming["date"] = datetime.strptime(incoming["date"], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        form = IncomingForm(data=incoming)
    else:
        post = request.POST.copy()
        post['amount'] = post['amount'].replace('.', '').replace(',', '.')
        form = IncomingForm(data=post)
        if form.is_valid():
            new_incoming = form.save(commit=False)
            db_incoming = api.update_incoming(new_incoming, incoming_id)
            return redirect('finance:incomings')

    context = {
        'form': form,
        'incoming': incoming
    }

    return render(request, 'finance/incomings/edit_incoming.html', context)

@login_required
def _get_monthly_expense_pend(request):
    """Retrive monthly expenses to show on index page"""
    monthly_expenses = api.get_all_monthly_expenses(page=1, limit=999, due_date=datetime.today().strftime("%Y-%m"), where="Pendente")["items"]

    if len(monthly_expenses) > 0:
        total_pend = round(sum(expense["amount"] for expense in monthly_expenses))
    else:
        monthly_expenses = api.get_all_monthly_expenses(page=1, limit=999, due_date=(datetime.today()+relativedelta(months=1)).strftime("%Y-%m"), where="Pendente")["items"]
        total_pend = round(sum(expense["amount"] for expense in monthly_expenses))

    return total_pend

@login_required
def expense_categorys(request):
    """Page to show all expense categorys"""

    page = int(request.GET.get('page') if request.GET.get('page') is not None else 1)
    limit = int(request.GET.get('limit') if request.GET.get('limit') is not None else 10)
    where = request.GET.get('where')
    categorys = api.get_all_expense_categorys(page, limit, "id desc", where)
    last_page = categorys["total_pages"]
    total_items = categorys["count"]
    pages = []

    if last_page <= 5:
        for i in range(1, last_page+1):
            pages.append(i)
    else:
        for i in range(1 if page <=5 else page - 4, 6 if page <= 5 else (page + 1)):
            pages.append(i)
    
    context = { 
        'categorys': categorys,
        'page': page,
        'pages': pages,
        'prev_page': page - 1,
        'next_page': page + 1,
        'last_page': last_page,
        'showing': f"{(page * limit) - (limit - 1)} a {(page * limit) if (page * limit) <= total_items else total_items } de {format(categorys['count'], ',d').replace(',', '.')}",
        'where': where
    }

    return render(request, 'finance/expense_categorys/expense_categorys.html', context)

@login_required
def new_expense_category(request):
    """Paga do add a new expense category"""
    if request.method != "POST":
        form = ExpenseCategoryForm()
    else:
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            new_category = form.save(commit=False)
            db_new_category = api.create_expense_category(new_category)
            return redirect('finance:expense_categorys')
        
    context = {"form": form}

    return render(request, 'finance/expense_categorys/new_expense_category.html', context)

@login_required
def edit_expense_category(request, category_id):
    """Page to edit a expense category"""
    if request.method != "POST":
        category = api.get_expense_category_by_id(category_id)["expense_category"]
        form = ExpenseCategoryForm(data=category)
    else:
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            new_category = form.save(commit=False)
            db_category = api.update_expense_category(new_category, category_id)
            return redirect('finance:expense_categorys')
        
    context = {
        'form': form,
        'category': category
    }

    return render(request, 'finance/expense_categorys/edit_expense_category.html', context)

@login_required
def import_fatura_santander(request):
    """Get expenses from credit card bill and import o database"""
    if request.method == "POST":
        file_data = request.FILES['file']
        
        # Save the uploaded file to a temporary location
        temp_file_path = os.path.join(f'{BASE_DIR}/setup/static/tmp', file_data.name)
        with open(temp_file_path, 'wb') as temp_file:
            for chunk in file_data.chunks():
                temp_file.write(chunk)
        try:
            data = read_pdf(temp_file_path, pages='all', pandas_options={'header': None}, area=[0, 0, 100, 100])

             # Calculate due date
            due_date_str = file_data.name.split('_')[0]
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')

            #Concat all tables
            print(data)
            table_expenses = pd.concat(data).dropna(how='all')

            #Remove rows that are not expenses
            table_expenses = table_expenses[table_expenses[0].str.contains('/')]
            table_expenses = table_expenses[~table_expenses[1].str.contains('Pagamento De Fatura')]

            #Create new formated columns
            table_expenses['date'] = pd.to_datetime(table_expenses[0], dayfirst=True, format='%d/%m/%Y')
            table_expenses['place'] = np.where(table_expenses[1].str.contains(r'.*\(.*', regex=True), table_expenses[1].str.split('(').str[0].str.strip(), table_expenses[1])
            table_expenses['description'] = table_expenses[1]
            table_expenses['amount'] = table_expenses[3].str.replace('R$', '').str.replace('.', '').str.replace(',', '.').astype(float)
            table_expenses['form_of_payment'] = 12
            table_expenses['expense_category'] = 24
            table_expenses['in_installments'] = table_expenses['place'].str.contains(r'.*\(.*\/.*\)', regex=True)
            table_expenses['plots'] = table_expenses[1].str.extract(r'\(\d+\/(\d+)\)', expand=False).fillna(1).astype(int)
            table_expenses['current_plot'] = table_expenses[1].str.extract(r'\((\d+)\/\d+\)', expand=False).fillna(1).astype(int)
            table_expenses['due_date'] = due_date

            #Remove columns that are not necessary
            table_expenses.drop([0, 1, 2, 3], inplace=True, axis=1)

            #Sort by date
            table_expenses.sort_values(by='date', inplace=True)
            
            #Create expenses
            for item in table_expenses.iterrows():
                expense = MonthlyExpense(
                    date = item[1]['date'],
                    place = item[1]['place'],
                    description = item[1]['description'],
                    amount = item[1]['amount'],
                    total_plots = item[1]['plots'],
                    current_plot = item[1]['current_plot'],
                    due_date = item[1]['due_date'],
                    form_of_payment_id = item[1]['form_of_payment'],
                    expense_category_id = item[1]['expense_category']
                )
                # api.create_monthly_expense(expense)
                # print(f"Expense created: {expense.description} - {expense.amount} - {expense.date} - {expense.due_date}")
            
            logger.info("Expenses were imported successfully.")
            return HttpResponse("Expenses were imported successfully.")
        except Exception as e:
            logger.error(f"Failed to import expenses: {e}")
            return HttpResponseBadRequest(f"Failed to import expenses: {e}")
        finally:
            os.remove(temp_file_path)

    return HttpResponseBadRequest("No file was uploaded.")

       



from datetime import datetime
import logging
import os
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
import numpy as np
import pandas as pd
from finance import api
from finance.models import MonthlyExpense
from finance.views.monthly_expenses import _get_monthly_expense_pend
from setup.settings import BASE_DIR
from tabula import read_pdf

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

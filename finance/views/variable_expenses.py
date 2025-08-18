
import logging
import csv
import io
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from finance import api
from finance.forms import VariableExpenseForm
from finance.open_finance import transactions
from ..finance_api import variable_expenses as api_variable_expenses

logger = logging.getLogger('finance')

@login_required
def import_variable_expenses_nubank(request):
    if request.method == "POST":
        csv_file = request.FILES.get('csv_file')
        if csv_file:
            # Aqui você pode ler o conteúdo do CSV
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string)
            next(reader, None) # Pula o cabeçalho
            expenses = []
            for row in reader:
                # Processar cada linha do CSV
                date = datetime.strptime(row[0], "%d/%m/%Y")
                amount = float(row[1])
                id_transaction = row[2]
                place = row[3]
                description = row[3]
                type = "DEBIT" if amount < 0 else "CREDIT"

                expense = {
                    "date": date.strftime("%Y-%m-%d"),  # Formato americano
                    "place": place,
                    "description": description,
                    "amount": abs(amount),
                    "id_transaction": id_transaction,
                    "form_of_payment": 29,
                    "type": type
                }

                expenses.append(expense)
                
            if len(expenses) > 0:
                # Aqui você pode salvar a despesa no banco de dados
                api_variable_expenses.bulk_create_variable_expenses(expenses, open_finance=True, form_of_payment_id=29, update_balance=False)
                messages.success(request, f"{len(expenses)} despesas importadas com sucesso do arquivo CSV.")
            else:
                messages.error(request, "Nenhuma despesa foi importada do arquivo CSV.")
        else:
            messages.error(request, "Nenhum arquivo CSV foi enviado.")

    return redirect("finance:variable_expenses")

@login_required
def sync_variable_expenses(request):
    """Sync variable expenses with external API"""
    # Retrieve all balances
    balances = api.get_all_balances()["balances"]
    for balance in balances:
        if not balance["id_connector"] or not balance["id_account_bank"]:
            continue

        # Retrieve the last variable expense for the balance
        last_variable_expense = api_variable_expenses.get_last_variable_expense_by_balance_id(balance["id"])
        if "error" in last_variable_expense:
            logger.error(f"Error retrieving last variable expense for balance_id {balance['id']}: {last_variable_expense['error']}")
            continue

        # Determine the from_date for the new variable expenses
        from_date = last_variable_expense["items"][0]["date"] if last_variable_expense["items"][0]["date"] < datetime.now().strftime("%Y-%m-%d %H:%M:%S") else datetime.today().strftime("%Y-%m-%d 00:00:00")

        # Retrieve new variable expenses from the transactions API
        new_variable_expenses = transactions.list(id_account=balance["id_account_bank"], id_item=balance["id_item"], from_date=from_date, pageSize=100)
        if "error" in new_variable_expenses:
            logger.error(f"Error retrieving new variable expenses for balance_id {balance['id']}: {new_variable_expenses['error']}")
            continue

        # Bulk create variable expenses
        expenses_created = api_variable_expenses.bulk_create_variable_expenses(new_variable_expenses["results"], True, last_variable_expense["items"][0]["form_of_payment_id"], False)
        
        if len(expenses_created) == len(new_variable_expenses["results"]):
            logger.info(f"Variable expenses created successfully for balance_id {balance['id']}")
        elif "error" in expenses_created:
            logger.error(f"Error creating variable expenses for balance_id {balance['id']}: {expenses_created['error']}")
            continue

    return redirect('finance:variable_expenses')

@login_required
def index(request):
    """Show all variable expenses"""
    page = int(request.GET.get('page') if request.GET.get('page') is not None else 1)
    limit = int(request.GET.get('limit') if request.GET.get('limit') is not None else 10)
    order_by = "variable_expenses.date desc"
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


    

    
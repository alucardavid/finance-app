import csv
import io
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from dateutil.relativedelta import relativedelta
from finance import api
from finance.forms import MonthlyExpenseForm
from finance.models import MonthlyExpense
from ..finance_api import monthly_expenses as api_monthly_expenses

meses_abreviados = {
    "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04",
    "MAI": "05", "JUN": "06", "JUL": "07", "AGO": "08",
    "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
}


@login_required
def index(request):
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
def import_monthly_expenses_nubank(request):
    """Import expenses from Nubank img files"""
    
    if request.method == "POST":
        file = request.FILES['csv_file']

        if not file.name.endswith('.csv'):
            messages.error(request, 'This is not a CSV file')
            return redirect('finance:monthly_expenses')

        try:
            decoded_file = file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.reader(io_string, delimiter=',')
            next(reader, None) # Skip the header
            expenses = []
            for row in reader:
                date = row[0]
                description = row[1]
                amount = row[2]
                mes = date.split('-')[1]
                dateParsed = datetime.strptime(date, "%Y-%m-%d").date()
                next_month = dateParsed + relativedelta(months=1)
                due_date = f"{next_month.year}-{next_month.month:02d}-08"
                
                expense = {
                    "date": date,
                    "amount": amount,
                    "description": description,
                    "place": description,
                    "total_plots": 1,
                    "current_plot": 1,
                    "form_of_payment_id": 14,
                    "expense_category_id": 24,
                    "due_date": due_date
                }
                expenses.append(expense)

        except Exception as e:
            return HttpResponseBadRequest(f"Error processing CSV: {str(e)}")

        # Create the expenses in bulk
        if expenses:
            expenses_created = api_monthly_expenses.bulk_create_monthly_expenses(expenses)

        # Check for errors
        if "error" in expenses_created:
            messages.error(request, f"Error creating monthly expenses: {expenses_created['error']}")
        elif expenses_created.status_code in [404, 400, 422]:
            messages.error(request, f"Error creating monthly expenses: {expenses_created.reason}")
            print(expenses_created.text)
        else:
            messages.success(request, f"{len(expenses)} Monthly expenses imported successfully.")

    return redirect('finance:monthly_expenses')

def _get_amount_from_nubank_csv(amount):
    """Extract amount from CSV results"""
    amount = float(amount.replace('RS', '').replace('R$', '').replace('.', '').replace(',', '.').replace('~', '-').replace(' ', '').strip())
    return amount

def _get_date_from_nubank_csv(date):
    """Extract date from CSV results"""
    dia = date.split(' ')[0]
    mes = meses_abreviados.get(date.split(' ')[1])

    return f"{datetime.now().year}-{mes}-{dia}"
    
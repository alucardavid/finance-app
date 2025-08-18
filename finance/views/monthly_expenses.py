
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from dateutil.relativedelta import relativedelta
from finance import api
from finance.forms import MonthlyExpenseForm
from finance.models import MonthlyExpense

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
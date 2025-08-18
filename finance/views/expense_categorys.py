from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from finance import api
from finance.forms import ExpenseCategoryForm

@login_required
def index(request):
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
    """Page to add a new expense category"""
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


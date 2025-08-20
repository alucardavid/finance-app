from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from finance import api
from finance.forms import IncomingForm

@login_required
def index(request):
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


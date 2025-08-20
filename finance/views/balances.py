from datetime import datetime
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from finance import api
from finance.forms import BalanceForm
from finance.open_finance import accounts
from django.contrib import messages

logger = logging.getLogger('finance')

@login_required
def index(request):
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
            new_balance.status_open_finance = new_balance.status_open_finance if new_balance.status_open_finance else "UPDATED"
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
        
        # Retrieve the account details from Open Finance API
        bank_account, status_open_finance = accounts.retrieve_account(balance["id_account_bank"], balance["id_item"])
        if "error" in bank_account:
            logger.error(f"Error retrieving account {balance['description']}: {bank_account['error']}")
            messages.error(request, f"Error retrieving account {balance['description']}: {bank_account['error']}")
            continue
        
        balance["value"] = bank_account["balance"]
        balance["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        balance["status_open_finance"] = status_open_finance
        updated_balance = api.update_balance(balance, balance["id"])
        if "error" in updated_balance:
            logger.error(f"Error updating balance {balance['id']}: {updated_balance['error']}")


    return redirect('finance:balances')

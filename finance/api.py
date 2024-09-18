"""Module to save api configs""" 
import sys
import requests
from datetime import datetime

host = "http://localhost:8001"

def get_all_balances():
    """Get all balances"""
    url = f"{host}/balances?order_by=value desc"

    try:
        response = requests.get(url)
        data = response.json()
        balances = []

        for balance in data:
            if balance["show"] == "S":
                balances.append(balance)
    except:
        balances = {}

    return { "balances": balances}

def get_balance_by_id(balance_id):
    """Get a balance by id"""
    url = f"{host}/balances/{balance_id}"

    try:
        response = requests.get(url)
        data = response.json()
        balance =  data
    except:
        balance = {}

    return { "balance": balance}

def create_balance(description, amount, show):
    """Create a new balance"""

    url = f"{host}/balances/"
    data = {
        'description': description,
        'value': str(amount),
        'show': show
    }

    try:
        response = requests.post(url, json= data)
        response_data = response.json()
        balance =  response_data
    except Exception as e:
        balance = {}

    return { "balance": balance}

def update_balance(new_balance, balance_id):    
    """Update a balance"""

    url = f"{host}/balances/{balance_id}"
    data = {
        'value': str(new_balance.value),
        'show': new_balance.show,
        'description': new_balance.description
    }

    try:
        response = requests.put(url, json= data)
        response_data = response.json()
        db_balance =  response_data
    except Exception as e:
        db_balance = {}

    return { "balance": db_balance}

def get_all_variable_expenses(limit: int = 15, order_by: str = "variable_expenses.id desc"):
    """Get all variable expenses"""

    url = f"{host}/variable-expenses?limit={limit}&order_by={order_by}"

    try:
        response = requests.get(url)
        data = response.json()
        variable_expenses = data
    except Exception as e:
        variable_expenses = {}

    return { "variable_expenses": variable_expenses}

def get_all_form_of_payments(show: str = "S", limit: int = 15, order_by: str = "form_of_payments.id desc"):
    """Get all form of payments"""
    url = f"{host}/form-of-payments?limit={limit}&order_by={order_by}"

    try:
        response = requests.get(url)
        data = response.json()
        form_of_payments = []
        
        for form in data:
            if form["active"] == "S":
                form_of_payments.append([form["id"], form["description"]])
    except Exception as e:
        form_of_payments = {}
    
    return { "form_of_payments": form_of_payments}

def create_variable_expense(new_variable_expense):
    """Create a new variable expense"""
    url = f"{host}/variable-expenses/"
    data = {
        'description': new_variable_expense.description,
        'place': new_variable_expense.place,
        'date': new_variable_expense.date.strftime("%Y-%m-%d"),
        'amount': str(new_variable_expense.amount),
        'type': new_variable_expense.type,
        'form_of_payment_id': new_variable_expense.form_of_payment.id
    }

    try:
        response = requests.post(url, json= data)
        response_data = response.json()
        db_variable_expense =  response_data
    except Exception as e:
        db_variable_expense = {}

    return { "variable_expense": db_variable_expense}

def get_variable_expense_by_id(variable_expense_id):
    """Get a variable expense by id"""
    url = f"{host}/variable-expenses/{variable_expense_id}"
    
    try:
        response = requests.get(url)
        data = response.json()
        variable_expense =  data
    except:
        variable_expense = {}

    return { "variable_expense": variable_expense}

def update_variable_expense(new_variable_expense, expense_id):
    """Update a variable expense"""

    url = f"{host}/variable-expenses/{expense_id}"
    data = {
        'description': new_variable_expense.description,
        'place': new_variable_expense.place,
        'date': new_variable_expense.date.strftime("%Y-%m-%d"),
        'amount': str(new_variable_expense.amount),
        'type': new_variable_expense.type,
        'form_of_payment_id': new_variable_expense.form_of_payment.id
    }

    try:
        response = requests.put(url, json= data)
        response_data = response.json()
        db_variable_expense =  response_data
    except Exception as e:
        db_variable_expense = {}

    return { "variable_expense": db_variable_expense}

def get_all_monthly_expenses(page:int = 1, limit: int = 10, order_by: str = "monthly_expenses.id desc"):
    """Get all monthly expenses"""
    url = f"{host}/monthly-expenses?limit={limit}&order_by={order_by}&page={page}"

    try:
        response = requests.get(url)
        data = response.json()
        expenses = data 
    
    except Exception as e:
        expenses = []

    return expenses
    
def create_monthly_expense(new_expense):
    """Create a new monthly expense"""
    url = f"{host}/monthly-expenses/"
    data = {
        'place': new_expense.place,
        'description': new_expense.description,
        'date': new_expense.date.strftime("%Y-%m-%d"),
        'due_date': new_expense.due_date.strftime("%Y-%m-%d"),
        'amount': str(new_expense.amount),
        'total_plots': new_expense.total_plots,
        'current_plot': new_expense.current_plot,
        'form_of_payment_id': new_expense.form_of_payment.id,
        'expense_category_id': 1
    }

    try:
        response =  requests.post(url, json= data)
        response_data = response.json()
        db_expense = response_data
    except Exception as e:
        db_expense = {}

    return { 'monthly_expense': db_expense}

def get_monthly_expense_by_id(expense_id):
    """Get a monthly expense by id"""
    url = f"{host}/monthly-expenses/{expense_id}"
    
    try:
        response = requests.get(url)
        data = response.json()
        expense =  data
    except:
        expense = {}

    return { "monthly_expense": expense}

def update_monthly_expense(new_expense, expense_id):
    """Update a monthly expense"""
    url = f"{host}/monthly-expenses/{expense_id}"
    data = {
        'place': new_expense.place,
        'description': new_expense.description,
        'date': new_expense.date.strftime("%Y-%m-%d"),
        'due_date': new_expense.due_date.strftime("%Y-%m-%d"),
        'amount': str(new_expense.amount),
        'total_plots': new_expense.total_plots,
        'current_plot': new_expense.current_plot,
        'form_of_payment_id': new_expense.form_of_payment.id,
        'expense_category_id': 1
    }

    try:
        response = requests.put(url, json= data)
        response_data = response.json()
        db_expense =  response_data
    except Exception as e:
        db_expense = {}

    return { "monthly_expense": db_expense}
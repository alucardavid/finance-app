import os
from venv import logger

import requests


host = os.getenv("API_HOST")


def get_last_variable_expense_by_balance_id(balance_id):
    """Retrieve the last variable expense from the API"""
    response = requests.get(f"{host}/variable-expenses/?balance_id={balance_id}&order_by=variable_expenses.date desc&limit=1")
    if response.status_code == 200:
        if len(response.json().get("items")) > 0:
            logger.info(f"Last variable expense retrieved for balance_id {balance_id}")
            return response.json()
        else:
            logger.error(f"No variable expense found for balance_id {balance_id}")
            return {"error": "No variable expense found"}

    logger.error(f"Error retrieving last variable expense for balance_id {balance_id}: {response.status_code}")
    return {"error": "Unable to retrieve last variable expense"}

def create_variable_expense(new_variable_expense, open_finance=False, form_of_payment_id=None, update_balance=False):
    """Create a new variable expense"""
    url = f"{host}/variable-expenses/?update_balance={update_balance}"
    payload = map_variable_expense(new_variable_expense, open_finance=open_finance, form_of_payment_id=form_of_payment_id)

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"Variable expense created successfully: {response_data}")
            response_data = response.json()
            return { "variable_expense": response_data}
        elif response.status_code == 409:
            logger.error(f"Variable expense already exists")
            return {"error": "Variable expense already exists"}
        elif response.status_code == 500:
            logger.error(f"Internal server error: {response.json().get('error', 'Unknown error')}")
            return {"error": response.json().get("error", "Unknown error")}
        else:
            logger.error(f"Error creating variable expense: {response_data.get('error', 'Unknown error')}")
            return {"error": response_data.get('error', 'Unknown error')}
    except Exception as e:
        db_variable_expense = {}
        return { "variable_expense": db_variable_expense, "error": str(e) }

def bulk_create_variable_expenses(expenses, open_finance=False, form_of_payment_id=None, update_balance=False):
    """Create multiple variable expenses"""
    url = f"{host}/variable-expenses/bulk/?update_balance={update_balance}"
    expenses_payload = [map_variable_expense(expense, open_finance=open_finance, form_of_payment_id=form_of_payment_id) for expense in expenses]

    try:
        response = requests.post(url, json=expenses_payload)
        if response.status_code == 200:
            logger.info(f"Variable expenses created successfully: {response.json()}")
            return response.json()
        elif response.status_code == 500:
            logger.error(f"Internal server error: {response.json().get('error', 'Unknown error')}")
            return {"error": "Unknown error"}
        else:
            logger.error(f"Error creating variable expenses: {response.json().get('error', 'Unknown error')}")
            return {"error": "Unknown error"}
    except Exception as e:
        db_variable_expenses = []
        return { "variable_expenses": db_variable_expenses, "error": str(e) }

def map_variable_expense(data, open_finance=False, form_of_payment_id=None):
    # If it comes from Open Finance API (different field names)
    if open_finance:
        return {
            "description": data["description"],
            "place": data["description"],
            "date": data.get("date", ""),
            "amount": abs(data.get("amount", 0)),
            "type": data.get("type", ""),
            "form_of_payment_id": form_of_payment_id,
            "id_transaction": data.get("id_transaction", "")
        }

    # If it comes from Django Form
    elif hasattr(data, "description"):
        return {
            "description": data.description,
            "place": data.place,
            "date": data.date,
            "amount": data.amount,
            "type": data.type,
            "form_of_payment_id": data.form_of_payment.id,
            "id_transaction": data.id_transaction
        }
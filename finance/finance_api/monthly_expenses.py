from datetime import datetime
import os

import requests
from finance import api

host = os.getenv("API_HOST")

def bulk_create_monthly_expenses(expenses):
    """Create multiple monthly expenses in the database."""
    url = f"{host}/monthly-expenses/bulk/"

    expenses.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
    
    try:
        response = requests.post(url, json=expenses)
        return response
    except Exception as e:
        return {"error": str(e)}
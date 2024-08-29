"""Module to save api configs""" 
import requests


host = "http://127.0.0.1:8001"


def get_all_balances():
    
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

    url = f"{host}/balances/{balance_id}"

    try:
        response = requests.get(url)
        data = response.json()
        balance =  data
    except:
        balance = {}

    return { "balance": balance}

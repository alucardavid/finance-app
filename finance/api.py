"""Module to save api configs""" 
import requests


host = "http://127.0.0.1:8001"


def get_all_balances():
    
    url = f"{host}/balances"

    try:
        response = requests.get(url)
        balances = response.json()
    except:
        balances = {}

    return { "balances": balances}



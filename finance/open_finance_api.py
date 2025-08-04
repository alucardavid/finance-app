from datetime import datetime, timedelta
import os
from time import time
import requests

host = os.getenv("OPEN_FINANCE_API_HOST")
client_id = os.getenv("OPEN_FINANCE_CLIENT_ID")
client_secret = os.getenv("OPEN_FINANCE_CLIENT_SECRET")
_token_cache = {
    "accessToken": None,
    "expiresIn": 0
}

_api_key = {
    "apiKey": None,
    "expiresIn": 0
}


def get_cached_token(connector_id):
    """ Retrieves a cached token if it exists and is still valid. """
    now = datetime.now()  # Get current time

    if _token_cache["accessToken"] and now < _token_cache["expiresIn"]:
        return _token_cache["accessToken"]
    
    token_data = get_token(connector_id)

    if "accessToken" in token_data:
        _token_cache["accessToken"] = token_data["accessToken"]
        _token_cache["expiresIn"] = now + timedelta(minutes=30)  # 30 min buffer
        return _token_cache["accessToken"]
    return None

def get_cached_api_key():
    """ Retrieves a cached API key if it exists. """
    now = datetime.now()  # Get current time

    if _api_key["apiKey"] and now < _api_key["expiresIn"]:
        return _api_key["apiKey"]

    api_key_data = create_api_key()

    if "error" in api_key_data:
        return {"error": api_key_data["error"]}
    
    if "apiKey" in api_key_data:
        _api_key["apiKey"] = api_key_data["apiKey"]
        _api_key["expiresIn"] = now + timedelta(hours=2)  # 2 hours buffer
        return _api_key["apiKey"]

    return None

def create_api_key():
    """
    Creates a new API key.
    """

    response = requests.post(f"{host}/auth", json={
        "clientId": client_id,
        "clientSecret": client_secret
    })
    if response.status_code == 200:
        return response.json()
    
    return {"error": "Failed to create API key"}

def create_connect_token(connector_id, api_key):
    """ Creates a connect token for the specified connector ID. """

    response = requests.post(f"{host}/connect_token", headers={
        "x-api-key": api_key
    }, json={
        "connector_id": connector_id,
        "paremeters": {
            "cpf": "39174716808"
        },
        "consentRedirectUrl": "https://your-redirect-url.com",
    })
    if response.status_code == 200:
        return response.json()
    
    return {"error": "Failed to create connect token"}

def get_token(connector_id):
    """ 
    Retrieves a connect token for the specified connector ID.
    """
    api_key = create_api_key()

    if api_key.get("error"):
        return {"error": api_key.get("error")}

    token = create_connect_token(612, api_key.get("apiKey"))
    if token.get("error"):
        return {"error": token.get("error")}
    
    return token

def retrieve_account(connector_id, id_account):
    api_key = get_cached_api_key()

    if "error" in api_key:
        return {"error": api_key.get("error")}

    response = requests.get(f"{host}/accounts/{id_account}", headers={
        "x-api-key": api_key
    })

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return {"error": "Account not found"}
    elif response.status_code == 400:
        return {"error": response.json()["message"]}
    
    return {"error": "Failed to retrieve account"}
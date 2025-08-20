import requests

from asyncio.log import logger
from finance.open_finance.auth import get_cached_api_key, host
from finance.open_finance import items


def retrieve_account(id_account, id_item):
    """ Retrieves account details from Open Finance API """

    # Get the cached API key
    api_key = get_cached_api_key()
    if "error" in api_key:
        return {"error": api_key.get("error")}, "ERROR"

    # Retrieve the item associated with the account
    # This is necessary to ensure the account is up-to-date
    item = items.retrieve(id_item)
    if item.get("status") in ["UPDATED", "OUTDATED"]:
        # Update the account before retrieving it
        items.update(id_item)

    # Retrieve the account details
    response = requests.get(f"{host}/accounts/{id_account}", headers={
        "x-api-key": api_key
    })

    if response.status_code == 200:
        logger.info(f"Account {id_account} retrieved successfully.")
        return response.json(), item.get("status")
    elif response.status_code == 404:
        logger.error(f"Account {id_account} not found.")
        return {"error": "Account not found"}, "ERROR"
    elif response.status_code == 400:
        logger.error(f"Failed to retrieve account {id_account}: {response.json().get('message', 'Unknown error')}")
        return {"error": response.json()["message"]}, "ERROR"
    
    logger.error(f"Unexpected error retrieving account {id_account}: {response.status_code} - {response.text}")
    return {"error": "Failed to retrieve account"}, "ERROR"
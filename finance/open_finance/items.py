import requests

from asyncio.log import logger
from finance.open_finance.auth import get_cached_api_key, host

def retrieve(id_item):
    """ Retrieves item details from Open Finance API """
    api_key = get_cached_api_key()
    
    if "error" in api_key:
        return {"error": api_key.get("error")}

    # Retrieve the item details
    response = requests.get(f"{host}/items/{id_item}", headers={
        "x-api-key": api_key
    })

    if response.status_code == 200:
        logger.info(f"Item {id_item} retrieved successfully.")
        return response.json()
    elif response.status_code == 404:
        logger.error(f"Item {id_item} not found.")
        return {"error": "Item not found"}
    elif response.status_code == 400:
        logger.error(f"Failed to retrieve item {id_item}: {response.json().get('message', 'Unknown error')}")
        return {"error": response.json()["message"]}
    
    return {"error": "Failed to retrieve item"}


def update(id_account):
    """ Sync account with the Open Finance Bank"""
    api_key = get_cached_api_key()
    
    if "error" in api_key:
        return {"error": api_key.get("error")}
    
    response = requests.patch(f"{host}/items/{id_account}", headers={
        "x-api-key": api_key
    })
    
    if response.status_code == 200:
        logger.info(f"Item {id_account} updated successfully.")
    elif response.status_code == 404:
        logger.error(f"Item {id_account} not found.")
    elif response.status_code == 400:
        logger.error(f"Failed to update item {id_account}: {response.json().get('message', 'Unknown error')}")
    else:
        logger.error(f"Unexpected error updating item {id_account}: {response.status_code} - {response.text}")
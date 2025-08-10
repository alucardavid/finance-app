
from asyncio.log import logger
import requests
from finance.open_finance.auth import get_cached_api_key, host


def list(id_account, from_date=None, pageSize=500):
    """List all transactions"""
    api_key = get_cached_api_key()
    if "error" in api_key:
            return {"error": api_key.get("error")}

    # Retrieve the item details
    response = requests.get(f"{host}/transactions?accountId={id_account}&from={from_date}&pageSize={pageSize}", headers={
        "x-api-key": api_key
    })

    if response.status_code == 200:
        logger.info(f"Retrieved transactions for account {id_account}")
        return response.json()
    if len(response.text) > 0 and "message" in response.json():
        logger.error(f"Error retrieving transactions for account {id_account}: {response.json().get('message')}")
        return {"error": response.json().get("message")}
    else:
        logger.error(f"Error retrieving transactions for account {id_account}: {response.text}")
        return {"error": response.text}

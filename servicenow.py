import requests
from requests.auth import HTTPBasicAuth
from config import *

BASE_URL = f"https://{SN_INSTANCE}.service-now.com/api/now/table/{TABLE}"

def get_auth():
    return HTTPBasicAuth(SN_USER, SN_PASS)

def create_ticket(data):
    response = requests.post(
        BASE_URL,
        auth=get_auth(),
        headers={"Content-Type": "application/json"},
        json=data,
    )
    return response

def get_all_tickets():
    response = requests.get(
        BASE_URL,
        auth=get_auth(),
        headers={"Accept": "application/json"},
    )

    return response.json()["result"]

def get_ticket(number):
    response = requests.get(
        f"{BASE_URL}?sysparm_query=number={number}",
        auth=get_auth(),
        headers={"Accept": "application/json"},
    )

    result = response.json()["result"]

    if len(result) > 0:
        return result[0]

    return None
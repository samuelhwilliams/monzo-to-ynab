import os

import flask
import requests


YNAB_BASE_URL = "https://api.youneedabudget.com/v1"
YNAB_TOKEN = os.environ["YNAB_TOKEN"]  # YNAB Personal Access Token
YNAB_BUDGET_ID = os.environ["YNAB_BUDGET_ID"]  # Budget ID as found in the URL with YNAB
YNAB_ACCOUNT_ID = os.environ["YNAB_ACCOUNT_ID"]  # Account ID under the specified YNAB Budget ID
MONZO_ACCOUNT_ID = os.environ["MONZO_ACCOUNT_ID"]  # Only process transactions from this account
MONZO_TOKEN = os.environ["MONZO_TOKEN"]  # Auth token provided to Monzo as the query param `token` in their webhook URL


def handle_monzo_transaction(data):
    cleared = False

    if data["type"] != "transaction.created":
        return f"Ignoring transaction type {data['type']}", 200

    transaction_data = data["data"]
    if transaction_data["account_id"] != MONZO_ACCOUNT_ID:
        return f"Ignoring transaction for account ID {transaction_data['account_id']}", 200

    if transaction_data["scheme"] == "uk_retail_pot":
        cleared = True if transaction_data["settled"] else False

    elif transaction_data["settled"]:
        # We don't have logic to de-dupe/match transactions
        # As a shortcut, we'll just create transactions when they're authorised, not when they're settled.
        # This might still create duplicates if Monzo's webhook fires multiple times for a single transaction.
        #
        # Pot transactions settle immediately beacause they're internal to Monzo; so we can ignore those.
        return f"Ignoring settled transaction", 200

    # TODO: Check if transaction already exists; if it does, update `cleared` status (and anything else?)

    ynab_data = {
        "transaction": {
            "account_id": YNAB_ACCOUNT_ID,
            "date": transaction_data["created"],
            "amount": transaction_data["amount"] * 10,  # YNAB wants this *10 ... for some reason
            "payee_name": transaction_data["description"],
            "memo": (transaction_data.get("merchant") or {}).get("name", ""),
            "cleared": "cleared" if cleared else "uncleared",
        }
    }

    response = requests.post(
        f"{YNAB_BASE_URL}/budgets/{YNAB_BUDGET_ID}/transactions",
        headers={"Authorization": f"Bearer {YNAB_TOKEN}"},
        json=ynab_data,
    )

    response_data = response.json()["data"]
    created_transactions = ",".join(response_data["transaction_ids"])

    return f"Created new transaction: {created_transactions}", 200


def main(request: flask.Request):
    if request.args.get("token") != MONZO_TOKEN:
        return "Unauthorized", 401

    data = request.json
    print(data)

    result = handle_monzo_transaction(data)
    print(result)

    return result

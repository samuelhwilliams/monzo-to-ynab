import os
from typing import Tuple

from dateutil.parser import parse as parse_datetime
import flask

from monzo_to_ynab.ynab import YnabClient
from monzo_to_ynab.monzo import MonzoClient
from monzo_to_ynab.transactions import Transaction, TransactionStatus


YNAB_TOKEN = os.environ["YNAB_TOKEN"]  # YNAB Personal Access Token
YNAB_BUDGET_ID = os.environ["YNAB_BUDGET_ID"]  # Budget ID as found in the URL with YNAB
YNAB_ACCOUNT_ID = os.environ["YNAB_ACCOUNT_ID"]  # Account ID under the specified YNAB Budget ID
MONZO_ACCOUNT_ID = os.environ["MONZO_ACCOUNT_ID"]  # Only process transactions from this account
MONZO_TOKEN = os.environ["MONZO_TOKEN"]  # Auth token provided to Monzo as the query param `token` in their webhook URL


def handle_monzo_transaction(transaction: Transaction) -> Tuple[str, int]:
    if transaction.status == TransactionStatus.settled:
        # We don't have logic to de-dupe/match transactions
        # As a shortcut, we'll just create transactions when they're authorised, not when they're settled.
        # This might still create duplicates if Monzo's webhook fires multiple times for a single transaction.
        #
        # Pot transactions settle immediately beacause they're internal to Monzo; so we can ignore those.
        return f"Ignoring settled transaction", 200

    # TODO: Check if transaction already exists; if it does, update `cleared` status (and anything else?)

    client = YnabClient(token=YNAB_TOKEN)

    new_transaction = client.create_transaction(
        budget_id=YNAB_BUDGET_ID, account_id=YNAB_ACCOUNT_ID, transaction=transaction
    )

    return f"Created new transaction: {new_transaction}", 200


def main(request: flask.Request) -> Tuple[str, int]:
    if request.args.get("token") != MONZO_TOKEN:
        return "Unauthorized", 401

    data = request.json
    print(f"Incoming data: {data}")

    if data["type"] != "transaction.created":
        print(f"Ignoring transaction type {data['type']}")
        return f"Ignoring transaction type {data['type']}", 200

    if data["data"]["account_id"] != MONZO_ACCOUNT_ID:
        print(f"Ignoring transaction for account ID {data['data']['account_id']}")
        return f"Ignoring transaction for account ID {data['data']['account_id']}", 200

    transaction = MonzoClient.parse_to_transaction(data)
    print(f"Parsed transaction: {transaction}")

    result = handle_monzo_transaction(data)
    print(f"Result: {result}")

    return result

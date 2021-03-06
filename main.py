import os
from typing import Tuple, Dict

import flask

from monzo_to_ynab.ynab import YnabClient
from monzo_to_ynab.monzo import MonzoClient
from monzo_to_ynab.transactions import Transaction
from monzo_to_ynab.utils import kms_decrypt


KMS_SECRET_RESOURCE_NAME = os.environ["KMS_SECRET_RESOURCE_NAME"]  # GCP KMS key to decrypt secrets
YNAB_TOKEN = kms_decrypt(
    KMS_SECRET_RESOURCE_NAME, os.environ["BASE64_KMS_ENCRYPTED_YNAB_TOKEN"]
)  # YNAB Personal Access Token
YNAB_BUDGET_ID = os.environ["YNAB_BUDGET_ID"]  # Budget ID as found in the URL with YNAB
YNAB_ACCOUNT_ID = os.environ["YNAB_ACCOUNT_ID"]  # Account ID under the specified YNAB Budget ID
MONZO_ACCOUNT_ID = os.environ["MONZO_ACCOUNT_ID"]  # Only process transactions from this account
MONZO_TOKEN = os.environ["MONZO_TOKEN"]  # Auth token provided to Monzo as the query param `token` in their webhook URL


def handle_monzo_transaction(transaction: Transaction) -> Tuple[str, int]:
    client = YnabClient(token=YNAB_TOKEN)

    transaction_id = client.find_existing_transaction(
        budget_id=YNAB_BUDGET_ID, account_id=YNAB_ACCOUNT_ID, transaction=transaction
    )
    if transaction_id:
        updated_transaction = client.update_transaction(
            budget_id=YNAB_BUDGET_ID, account_id=YNAB_ACCOUNT_ID, transaction_id=transaction_id, transaction=transaction
        )

        return f"Updated existing transaction: {updated_transaction}", 200

    else:
        new_transaction = client.create_transaction(
            budget_id=YNAB_BUDGET_ID, account_id=YNAB_ACCOUNT_ID, transaction=transaction
        )

        return f"Created new transaction: {new_transaction}", 200


def main(request: flask.Request) -> Tuple[str, int]:
    if request.args.get("token") != MONZO_TOKEN:
        print("Unauthorized", 401)
        return "Unauthorized", 401

    data: Dict = request.json
    print(f"Incoming data: {data}")

    if data["type"] != "transaction.created":
        print(f"Ignoring transaction type {data['type']}", 200)
        return f"Ignoring transaction type {data['type']}", 200

    transaction_data: Dict = data["data"]
    if "decline_reason" in transaction_data:
        print("Ignoring declined transaction", 200)
        return "Ignoring declined transaction", 200

    if transaction_data["account_id"] != MONZO_ACCOUNT_ID:
        print(f"Ignoring transaction for different account ID {data['data']['account_id']}", 200)
        return f"Ignoring transaction for different account ID {data['data']['account_id']}", 200

    if transaction_data["amount"] == 0 and transaction_data["notes"] == "Active card check":
        print(f"Ignoring active card check", 200)
        return f"Ignoring active card check", 200

    transaction: Transaction = MonzoClient.parse_to_transaction(transaction_data)
    print(f"Parsed transaction: {transaction}")

    result = handle_monzo_transaction(transaction)
    print(f"Result: {result}")

    return result

import os
from typing import Tuple, Dict

import flask
from flask import request

from monzo_to_ynab.ynab import YnabClient
from monzo_to_ynab.monzo import MonzoClient
from monzo_to_ynab.transactions import Transaction


MONZO_TO_YNAB_CONFIG = os.environ['MONZO_TO_YNAB_CONFIG']


def handle_monzo_transaction(transaction: Transaction, ynab_token, ynab_budget_id, ynab_account_id) -> Tuple[str, int]:
    client = YnabClient(token=ynab_token)

    transaction_id = client.find_existing_transaction(
        budget_id=ynab_budget_id, account_id=ynab_account_id, transaction=transaction
    )
    if transaction_id:
        updated_transaction = client.update_transaction(
            budget_id=ynab_budget_id, account_id=ynab_account_id, transaction_id=transaction_id, transaction=transaction
        )

        return f"Updated existing transaction: {updated_transaction}", 200

    else:
        new_transaction = client.create_transaction(
            budget_id=ynab_budget_id, account_id=ynab_account_id, transaction=transaction
        )

        return f"Created new transaction: {new_transaction}", 200


app = flask.Flask(__name__)


@app.route('/', methods=['POST'])
def main() -> Tuple[str, int]:
    token = request.args.get("token")
    if token not in MONZO_TO_YNAB_CONFIG:
        print("Unauthorized", 401)
        return "Unauthorized", 401
    
    config = MONZO_TO_YNAB_CONFIG[token]
    ynab_token = config['ynab-token']
    ynab_budget_id = config['ynab-budget-id']
    ynab_account_id = config['ynab-account-id']
    monzo_account_id = config['monzo-account-id']

    data: Dict = request.json
    print(f"Incoming data: {data}")

    if data["type"] != "transaction.created":
        print(f"Ignoring transaction type {data['type']}", 200)
        return f"Ignoring transaction type {data['type']}", 200

    transaction_data: Dict = data["data"]
    if "decline_reason" in transaction_data:
        print("Ignoring declined transaction", 200)
        return "Ignoring declined transaction", 200

    if transaction_data["account_id"] != monzo_account_id:
        print(f"Ignoring transaction for different account ID {data['data']['account_id']}", 200)
        return f"Ignoring transaction for different account ID {data['data']['account_id']}", 200

    if transaction_data["amount"] == 0 and transaction_data["notes"] == "Active card check":
        print(f"Ignoring active card check", 200)
        return f"Ignoring active card check", 200

    transaction: Transaction = MonzoClient.parse_to_transaction(transaction_data)
    print(f"Parsed transaction: {transaction}")

    result = handle_monzo_transaction(transaction, ynab_token, ynab_budget_id, ynab_account_id)
    print(f"Result: {result}")

    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000))
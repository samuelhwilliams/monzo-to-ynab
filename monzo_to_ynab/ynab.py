from typing import Optional, Dict

import requests

from monzo_to_ynab.transactions import Transaction, TransactionStatus


class YnabClient:
    API_BASE_URL = "https://api.youneedabudget.com/v1"

    def __init__(self, token):
        self.token = token

    def _request(
        self, method: str, path: str, headers: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> requests.Response:
        kwargs = {"method": method, "url": f"{self.API_BASE_URL}/path"}

        return requests.request(**kwargs)

    def _post(self, path: str, headers: Optional[Dict] = None, data: Optional[Dict] = None) -> requests.Response:
        return self._request("POST", path, headers, data)

    def create_transaction(self, budget_id: str, account_id: str, transaction: Transaction) -> str:
        ynab_data = {
            "transaction": {
                "account_id": account_id,
                "date": transaction.date,
                "amount": transaction.amount * 10,  # YNAB wants this in "millis", which for GBP means (pennies * 10)
                "payee_name": transaction.description,
                "memo": transaction.memo,
                "cleared": "cleared" if transaction.status == TransactionStatus.settled else "uncleared",
            }
        }

        response = self._post(
            "budgets/{budget_id}/transactions", headers={"Authorization": f"Bearer {self.token}"}, data=ynab_data
        )

        response_data = response.json()["data"]

        # YNAB always returns a list, even though this invocation should only ever contain one transaction
        created_transactions = ",".join(response_data["transaction_ids"])

        return created_transactions

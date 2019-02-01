from typing import Optional, Dict, Any

import backoff
from dateutil.parser import parse as parse_datetime
import requests
from requests.exceptions import RequestException

from monzo_to_ynab.transactions import Transaction, TransactionStatus
from monzo_to_ynab.request_auth import HTTPBearerAuth


class YnabClient:
    API_BASE_URL = "https://api.youneedabudget.com/v1"

    def __init__(self, token):
        self.token = token

    @backoff.on_exception(wait_gen=backoff.constant, exception=RequestException)
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        auth = HTTPBearerAuth(token=self.token)
        if "auth" in kwargs:
            auth = kwargs.pop("auth")

        return requests.request(method=method, url=f"{self.API_BASE_URL}/{path}", auth=auth, **kwargs)

    def _get(self, path: str, **kwargs) -> requests.Response:
        return self._request(method="GET", path=path, **kwargs)

    def _post(self, path: str, **kwargs) -> requests.Response:
        return self._request(method="POST", path=path, **kwargs)

    def _put(self, path: str, **kwargs) -> requests.Response:
        return self._request(method="PUT", path=path, **kwargs)

    @classmethod
    def parse_to_transaction(self, data: Dict[str, Any]) -> Transaction:
        match_id = data["import_id"]
        date = parse_datetime(data["date"])
        amount = data["amount"] / 10
        description = data["payee_name"]
        status = TransactionStatus.authorized if data["cleared"] == "uncleared" else TransactionStatus.settled

        transaction = Transaction(match_id=match_id, date=date, amount=amount, description=description, status=status)

        return transaction

    @classmethod
    def json_from_transaction(cls, account_id: str, transaction: Transaction) -> Dict[str, Any]:
        return {
            "transaction": {
                "import_id": transaction.match_id,
                "account_id": account_id,
                "date": transaction.date.isoformat(),
                "amount": transaction.amount * 10,  # YNAB wants this in "millis", which for GBP means (pennies * 10)
                "payee_name": transaction.description,
                "cleared": "cleared" if transaction.status == TransactionStatus.settled else "uncleared",
            }
        }

    def create_transaction(self, budget_id: str, account_id: str, transaction: Transaction) -> str:
        response = self._post(
            path=f"budgets/{budget_id}/transactions",
            json=self.json_from_transaction(account_id=account_id, transaction=transaction),
        )

        response_data = response.json()["data"]

        # YNAB always returns a list, even though this invocation should only ever contain one transaction
        created_transactions = ",".join(response_data["transaction_ids"])

        return created_transactions

    def find_existing_transaction(self, budget_id: str, account_id: str, transaction: Transaction) -> Optional[str]:
        params = {"since_date": transaction.date.date().isoformat()}
        response = self._get(path=f"budgets/{budget_id}/accounts/{account_id}/transactions", params=params)
        print(f"Response from YNAB: {response.json()}")

        print(f"Comparing YNAB transactions:")
        print(f"  {str(transaction)}")

        for ynab_transaction_data in response.json()["data"]["transactions"]:
            ynab_transaction = self.parse_to_transaction(ynab_transaction_data)

            print(f"    {str(ynab_transaction)}", end="")
            if transaction == ynab_transaction:
                print(" -> Match")
                return ynab_transaction_data["id"]

            print(" -> No match")

        return None

    def update_transaction(self, budget_id: str, account_id: str, transaction_id: str, transaction: Transaction) -> str:
        response = self._put(
            path=f"budgets/{budget_id}/transactions/{transaction_id}",
            json=self.json_from_transaction(account_id, transaction),
        )

        return response.json()["data"]["transaction"]["id"]

from typing import Dict, Any

from dateutil.parser import parse as parse_datetime

from monzo_to_ynab.transactions import Transaction, TransactionStatus


class MonzoClient:
    @classmethod
    def parse_to_transaction(cls, data: Dict[str, Any]) -> Transaction:
        date = parse_datetime(data["created_at"])
        amount = data["amount"]
        description = data["description"]
        memo = (data.get("merchant") or {}).get("name", "")
        status = TransactionStatus.settled if data["settled"] else TransactionStatus.authorized

        transaction = Transaction(date=date, amount=amount, description=description, memo=memo, status=status)

        return transaction

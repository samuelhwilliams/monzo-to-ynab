from typing import Dict, Any

from dateutil.parser import parse as parse_datetime

from monzo_to_ynab.transactions import Transaction, TransactionStatus


class MonzoClient:
    @classmethod
    def parse_to_transaction(cls, data: Dict[str, Any]) -> Transaction:
        match_id = data["id"]
        date = parse_datetime(data["created"])
        amount = data["amount"]
        description = (data.get("merchant") or {}).get("name", "") or data["description"]
        status = TransactionStatus.settled if data["settled"] else TransactionStatus.authorized

        transaction = Transaction(match_id=match_id, date=date, amount=amount, description=description, status=status)

        return transaction

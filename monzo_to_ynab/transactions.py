from dataclasses import dataclass
from datetime import datetime
import enum


class TransactionStatus(enum.Enum):
    authorized = "authorized"
    settled = "settled"


@dataclass
class Transaction:
    match_id: str  # An arbitrary string that determines when two transactions are equivalent (__eq__)
    date: datetime  # When the transaction took place
    amount: int  # The value of the transaction in base units of the currency
    description: str  # A description for the transaction, generally the name of the merchant
    status: TransactionStatus  # Whether the transaction is authorized, settled, etc (refunded?)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return bool(self.match_id and other.match_id and self.match_id == other.match_id)

        return False

    def __str__(self):
        return (
            f"{self.amount} with '{self.description}' on {self.date.isoformat()} "
            f"[status={self.status.value}] "
            f"{{match_id={self.match_id}}}"
        )

from dataclasses import dataclass
from datetime import datetime
import enum


class TransactionStatus(enum.Enum):
    authorized = "authorized"
    settled = "settled"


@dataclass
class Transaction:
    date: datetime
    amount: int
    description: str
    memo: str
    status: TransactionStatus

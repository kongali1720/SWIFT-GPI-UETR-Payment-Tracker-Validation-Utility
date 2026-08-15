from collections import Counter
from typing import Iterable

from src.tracker.payment import Payment


def status_summary(
    payments: Iterable[Payment],
) -> dict[str, int]:

    counter = Counter(
        payment.status.value
        for payment in payments
    )

    return dict(counter)


def total_amount(
    payments: Iterable[Payment],
) -> float:

    return sum(
        payment.amount
        for payment in payments
    )

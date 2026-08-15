from typing import Dict, List, Optional

from src.tracker.payment import Payment


class PaymentRepository:
    """
    In-memory payment repository.

    Designed as a clean abstraction so a persistent database
    can be introduced later without changing business logic.
    """

    def __init__(self) -> None:
        self._payments: Dict[str, Payment] = {}

    def create(self, payment: Payment) -> Payment:
        if payment.uetr in self._payments:
            raise ValueError(
                f"Payment already exists: {payment.uetr}"
            )

        self._payments[payment.uetr] = payment

        return payment

    def get(self, uetr: str) -> Optional[Payment]:
        return self._payments.get(uetr)

    def update(self, payment: Payment) -> Payment:
        if payment.uetr not in self._payments:
            raise KeyError(
                f"Payment not found: {payment.uetr}"
            )

        self._payments[payment.uetr] = payment

        return payment

    def delete(self, uetr: str) -> bool:
        if uetr not in self._payments:
            return False

        del self._payments[uetr]

        return True

    def list_all(self) -> List[Payment]:
        return list(self._payments.values())

    def count(self) -> int:
        return len(self._payments)

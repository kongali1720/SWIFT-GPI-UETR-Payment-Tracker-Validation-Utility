from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List

from src.tracker.payment import Payment, PaymentStatus


ALLOWED_TRANSITIONS = {
    PaymentStatus.CREATED: {
        PaymentStatus.VALIDATED,
        PaymentStatus.FAILED,
    },
    PaymentStatus.VALIDATED: {
        PaymentStatus.PROCESSING,
        PaymentStatus.FAILED,
    },
    PaymentStatus.PROCESSING: {
        PaymentStatus.IN_PROGRESS,
        PaymentStatus.FAILED,
    },
    PaymentStatus.IN_PROGRESS: {
        PaymentStatus.COMPLETED,
        PaymentStatus.FAILED,
    },
    PaymentStatus.COMPLETED: set(),
    PaymentStatus.FAILED: set(),
}


@dataclass
class PaymentEvent:
    uetr: str
    previous_status: PaymentStatus
    new_status: PaymentStatus
    timestamp: datetime
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "uetr": self.uetr,
            "previous_status": self.previous_status.value,
            "new_status": self.new_status.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
        }


class PaymentWorkflow:
    """
    Controls authorized payment workflow transitions.

    This engine is local and deterministic. It does not connect
    to SWIFT infrastructure or external banking systems.
    """

    def __init__(self) -> None:
        self.events: List[PaymentEvent] = []

    def can_transition(
        self,
        current: PaymentStatus,
        target: PaymentStatus,
    ) -> bool:
        return target in ALLOWED_TRANSITIONS.get(
            current,
            set(),
        )

    def transition(
        self,
        payment: Payment,
        target: PaymentStatus,
        reason: str = "",
    ) -> PaymentEvent:

        current = payment.status

        if not self.can_transition(current, target):
            raise ValueError(
                f"Invalid payment transition: "
                f"{current.value} -> {target.value}"
            )

        payment.update_status(target)

        event = PaymentEvent(
            uetr=payment.uetr,
            previous_status=current,
            new_status=target,
            timestamp=datetime.now(timezone.utc),
            reason=reason,
        )

        self.events.append(event)

        return event

    def history(self, uetr: str) -> list[PaymentEvent]:
        return [
            event
            for event in self.events
            if event.uetr == uetr
        ]

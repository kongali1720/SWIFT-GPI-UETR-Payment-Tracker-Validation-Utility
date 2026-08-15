from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class PaymentStatus(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class Payment:
    uetr: str
    amount: float
    currency: str
    origin: str
    destination: str

    status: PaymentStatus = PaymentStatus.CREATED

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: Optional[datetime] = None

    def update_status(self, status: PaymentStatus) -> None:
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "uetr": self.uetr,
            "amount": self.amount,
            "currency": self.currency,
            "origin": self.origin,
            "destination": self.destination,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": (
                self.updated_at.isoformat()
                if self.updated_at
                else None
            ),
        }

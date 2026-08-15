from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List


@dataclass
class AuditRecord:
    event_type: str
    uetr: str
    message: str
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "uetr": self.uetr,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
        }


class AuditLogger:
    """
    Lightweight in-memory audit logger.

    Production deployments can replace this implementation
    with a database, message queue, or centralized logging system.
    """

    def __init__(self) -> None:
        self._records: List[AuditRecord] = []

    def record(
        self,
        event_type: str,
        uetr: str,
        message: str,
    ) -> AuditRecord:

        record = AuditRecord(
            event_type=event_type,
            uetr=uetr,
            message=message,
            timestamp=datetime.now(timezone.utc),
        )

        self._records.append(record)

        return record

    def get_by_uetr(
        self,
        uetr: str,
    ) -> List[AuditRecord]:

        return [
            record
            for record in self._records
            if record.uetr == uetr
        ]

    def all(self) -> List[AuditRecord]:
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

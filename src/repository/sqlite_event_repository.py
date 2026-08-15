from typing import List

from src.database.sqlite import SQLiteDatabase
from src.tracker.workflow import PaymentEvent


class SQLiteEventRepository:
    """
    Persistent repository for payment workflow events.
    """

    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def save(self, event: PaymentEvent) -> PaymentEvent:
        self.database.connection.execute(
            """
            INSERT INTO payment_events (
                uetr,
                previous_status,
                new_status,
                timestamp,
                reason
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event.uetr,
                event.previous_status.value,
                event.new_status.value,
                event.timestamp.isoformat(),
                event.reason,
            ),
        )

        self.database.connection.commit()

        return event

    def get_by_uetr(
        self,
        uetr: str,
    ) -> List[dict]:
        rows = self.database.connection.execute(
            """
            SELECT
                id,
                uetr,
                previous_status,
                new_status,
                timestamp,
                reason
            FROM payment_events
            WHERE uetr = ?
            ORDER BY id ASC
            """,
            (uetr,),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def count(self) -> int:
        row = self.database.connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM payment_events
            """
        ).fetchone()

        return int(row["count"])

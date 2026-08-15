from typing import List

from src.audit.audit_log import AuditRecord
from src.database.sqlite import SQLiteDatabase


class SQLiteAuditRepository:
    """
    Persistent repository for audit records.
    """

    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def save(self, record: AuditRecord) -> AuditRecord:
        self.database.connection.execute(
            """
            INSERT INTO audit_logs (
                event_type,
                uetr,
                message,
                timestamp
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                record.event_type,
                record.uetr,
                record.message,
                record.timestamp.isoformat(),
            ),
        )

        self.database.connection.commit()

        return record

    def get_by_uetr(
        self,
        uetr: str,
    ) -> List[dict]:
        rows = self.database.connection.execute(
            """
            SELECT
                id,
                event_type,
                uetr,
                message,
                timestamp
            FROM audit_logs
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
            FROM audit_logs
            """
        ).fetchone()

        return int(row["count"])

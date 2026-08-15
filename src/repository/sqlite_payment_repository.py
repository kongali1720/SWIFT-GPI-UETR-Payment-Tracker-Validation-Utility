from datetime import datetime
from typing import List, Optional

from src.database.sqlite import SQLiteDatabase
from src.tracker.payment import Payment, PaymentStatus


class SQLitePaymentRepository:
    """
    Persistent payment repository backed by SQLite.
    """

    def __init__(self, database: SQLiteDatabase):
        self.database = database

    def create(self, payment: Payment) -> Payment:
        try:
            self.database.connection.execute(
                """
                INSERT INTO payments (
                    uetr,
                    amount,
                    currency,
                    origin,
                    destination,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payment.uetr,
                    payment.amount,
                    payment.currency,
                    payment.origin,
                    payment.destination,
                    payment.status.value,
                    payment.created_at.isoformat(),
                    (
                        payment.updated_at.isoformat()
                        if payment.updated_at
                        else None
                    ),
                ),
            )

            self.database.connection.commit()

        except Exception:
            self.database.connection.rollback()
            raise

        return payment

    def get(self, uetr: str) -> Optional[Payment]:
        row = self.database.connection.execute(
            """
            SELECT
                uetr,
                amount,
                currency,
                origin,
                destination,
                status,
                created_at,
                updated_at
            FROM payments
            WHERE uetr = ?
            """,
            (uetr,),
        ).fetchone()

        if row is None:
            return None

        return self._row_to_payment(row)

    def update(self, payment: Payment) -> Payment:
        cursor = self.database.connection.execute(
            """
            UPDATE payments
            SET
                amount = ?,
                currency = ?,
                origin = ?,
                destination = ?,
                status = ?,
                created_at = ?,
                updated_at = ?
            WHERE uetr = ?
            """,
            (
                payment.amount,
                payment.currency,
                payment.origin,
                payment.destination,
                payment.status.value,
                payment.created_at.isoformat(),
                (
                    payment.updated_at.isoformat()
                    if payment.updated_at
                    else None
                ),
                payment.uetr,
            ),
        )

        if cursor.rowcount == 0:
            self.database.connection.rollback()

            raise KeyError(
                f"Payment not found: {payment.uetr}"
            )

        self.database.connection.commit()

        return payment

    def delete(self, uetr: str) -> bool:
        cursor = self.database.connection.execute(
            """
            DELETE FROM payments
            WHERE uetr = ?
            """,
            (uetr,),
        )

        self.database.connection.commit()

        return cursor.rowcount > 0

    def list_all(self) -> List[Payment]:
        rows = self.database.connection.execute(
            """
            SELECT
                uetr,
                amount,
                currency,
                origin,
                destination,
                status,
                created_at,
                updated_at
            FROM payments
            ORDER BY created_at ASC
            """
        ).fetchall()

        return [
            self._row_to_payment(row)
            for row in rows
        ]

    def count(self) -> int:
        row = self.database.connection.execute(
            "SELECT COUNT(*) AS count FROM payments"
        ).fetchone()

        return int(row["count"])

    @staticmethod
    def _row_to_payment(row) -> Payment:
        updated_at = (
            datetime.fromisoformat(row["updated_at"])
            if row["updated_at"]
            else None
        )

        return Payment(
            uetr=row["uetr"],
            amount=float(row["amount"]),
            currency=row["currency"],
            origin=row["origin"],
            destination=row["destination"],
            status=PaymentStatus(row["status"]),
            created_at=datetime.fromisoformat(
                row["created_at"]
            ),
            updated_at=updated_at,
        )

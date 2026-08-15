import sqlite3
from pathlib import Path
from typing import Union


DatabasePath = Union[str, Path]


class SQLiteDatabase:
    """
    Lightweight SQLite database manager.

    The database is intentionally implemented behind a small
    abstraction so the application can later migrate to PostgreSQL
    without coupling business logic to SQLite.
    """

    def __init__(self, path: DatabasePath = "data/swift_gpi_uetr.db"):
        self.path = str(path)

        if self.path != ":memory:":
            Path(self.path).parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        self.connection = sqlite3.connect(
            self.path,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self.initialize()

    def initialize(self) -> None:
        cursor = self.connection.cursor()

        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS payments (
                uetr TEXT PRIMARY KEY,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS payment_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uetr TEXT NOT NULL,
                previous_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                reason TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (uetr)
                    REFERENCES payments(uetr)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                uetr TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_payment_events_uetr
                ON payment_events(uetr);

            CREATE INDEX IF NOT EXISTS idx_audit_logs_uetr
                ON audit_logs(uetr);
            """
        )

        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

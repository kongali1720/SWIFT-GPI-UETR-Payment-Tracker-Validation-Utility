from datetime import datetime, timezone

from src.audit.audit_log import AuditRecord
from src.database.sqlite import SQLiteDatabase
from src.repository.sqlite_audit_repository import SQLiteAuditRepository


UETR = "550e8400-e29b-41d4-a716-446655440021"


def test_save_and_get_audit(tmp_path):
    database = SQLiteDatabase(
        tmp_path / "audit.db"
    )

    repository = SQLiteAuditRepository(database)

    record = AuditRecord(
        event_type="PAYMENT_CREATED",
        uetr=UETR,
        message="Payment created",
        timestamp=datetime.now(timezone.utc),
    )

    repository.save(record)

    records = repository.get_by_uetr(UETR)

    assert len(records) == 1
    assert records[0]["event_type"] == "PAYMENT_CREATED"
    assert records[0]["uetr"] == UETR
    assert records[0]["message"] == "Payment created"

    database.close()

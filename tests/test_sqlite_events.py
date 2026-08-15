from datetime import datetime, timezone

from src.database.sqlite import SQLiteDatabase
from src.repository.sqlite_event_repository import SQLiteEventRepository
from src.tracker.payment import PaymentStatus
from src.tracker.workflow import PaymentEvent


UETR = "550e8400-e29b-41d4-a716-446655440020"


def test_save_and_get_event(tmp_path):
    database = SQLiteDatabase(
        tmp_path / "events.db"
    )

    repository = SQLiteEventRepository(database)

    event = PaymentEvent(
        uetr=UETR,
        previous_status=PaymentStatus.CREATED,
        new_status=PaymentStatus.VALIDATED,
        timestamp=datetime.now(timezone.utc),
        reason="Validation successful",
    )

    repository.save(event)

    events = repository.get_by_uetr(UETR)

    assert len(events) == 1
    assert events[0]["uetr"] == UETR
    assert events[0]["previous_status"] == "CREATED"
    assert events[0]["new_status"] == "VALIDATED"
    assert events[0]["reason"] == "Validation successful"

    database.close()

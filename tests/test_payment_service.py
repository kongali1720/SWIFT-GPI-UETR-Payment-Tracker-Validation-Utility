from src.audit.audit_log import AuditLogger
from src.database.sqlite import SQLiteDatabase
from src.repository.sqlite_audit_repository import SQLiteAuditRepository
from src.repository.sqlite_event_repository import SQLiteEventRepository
from src.repository.sqlite_payment_repository import SQLitePaymentRepository
from src.services.payment_service import PaymentService
from src.tracker.payment import Payment, PaymentStatus
from src.tracker.workflow import PaymentWorkflow


UETR = "550e8400-e29b-41d4-a716-446655440022"


def create_service(tmp_path):
    database = SQLiteDatabase(
        tmp_path / "service.db"
    )

    payment_repository = SQLitePaymentRepository(
        database
    )

    event_repository = SQLiteEventRepository(
        database
    )

    audit_repository = SQLiteAuditRepository(
        database
    )

    service = PaymentService(
        payment_repository=payment_repository,
        workflow=PaymentWorkflow(),
        audit_logger=AuditLogger(),
        event_repository=event_repository,
        audit_repository=audit_repository,
    )

    return database, service


def create_payment():
    return Payment(
        uetr=UETR,
        amount=50000.0,
        currency="USD",
        origin="SYSTEM_A",
        destination="SYSTEM_B",
    )


def test_service_create_payment(tmp_path):
    database, service = create_service(tmp_path)

    payment = service.create_payment(
        create_payment()
    )

    assert payment.uetr == UETR
    assert service.get_payment(UETR) is not None

    database.close()


def test_service_status_and_events(tmp_path):
    database, service = create_service(tmp_path)

    service.create_payment(
        create_payment()
    )

    service.update_status(
        service.get_payment(UETR),
        PaymentStatus.VALIDATED,
        "Validation successful",
    )

    service.update_status(
        service.get_payment(UETR),
        PaymentStatus.PROCESSING,
        "Processing started",
    )

    events = service.get_events(UETR)

    assert len(events["workflow_events"]) == 2
    assert len(events["audit_events"]) >= 3

    stored = service.get_payment(UETR)

    assert stored.status == PaymentStatus.PROCESSING

    database.close()


def test_service_persistence_after_reopen(tmp_path):
    database_path = tmp_path / "persistent-service.db"

    database = SQLiteDatabase(
        database_path
    )

    service = PaymentService(
        payment_repository=SQLitePaymentRepository(
            database
        ),
        workflow=PaymentWorkflow(),
        audit_logger=AuditLogger(),
        event_repository=SQLiteEventRepository(
            database
        ),
        audit_repository=SQLiteAuditRepository(
            database
        ),
    )

    service.create_payment(
        create_payment()
    )

    service.update_status(
        service.get_payment(UETR),
        PaymentStatus.VALIDATED,
        "Validation successful",
    )

    database.close()

    reopened = SQLiteDatabase(
        database_path
    )

    reopened_service = PaymentService(
        payment_repository=SQLitePaymentRepository(
            reopened
        ),
        workflow=PaymentWorkflow(),
        audit_logger=AuditLogger(),
        event_repository=SQLiteEventRepository(
            reopened
        ),
        audit_repository=SQLiteAuditRepository(
            reopened
        ),
    )

    payment = reopened_service.get_payment(
        UETR
    )

    events = reopened_service.get_events(
        UETR
    )

    assert payment is not None
    assert payment.status == PaymentStatus.VALIDATED
    assert len(events["workflow_events"]) == 1
    assert len(events["audit_events"]) >= 2

    reopened.close()

from src.audit.audit_log import AuditLogger


UETR = "550e8400-e29b-41d4-a716-446655440000"


def test_create_audit_record():
    logger = AuditLogger()

    record = logger.record(
        event_type="PAYMENT_CREATED",
        uetr=UETR,
        message="Payment created successfully",
    )

    assert record.event_type == "PAYMENT_CREATED"
    assert record.uetr == UETR
    assert record.message == "Payment created successfully"


def test_get_audit_records_by_uetr():
    logger = AuditLogger()

    logger.record(
        event_type="PAYMENT_CREATED",
        uetr=UETR,
        message="Payment created",
    )

    logger.record(
        event_type="STATUS_CHANGED",
        uetr=UETR,
        message="Payment moved to PROCESSING",
    )

    records = logger.get_by_uetr(UETR)

    assert len(records) == 2


def test_audit_count():
    logger = AuditLogger()

    logger.record(
        event_type="PAYMENT_CREATED",
        uetr=UETR,
        message="Payment created",
    )

    assert logger.count() == 1

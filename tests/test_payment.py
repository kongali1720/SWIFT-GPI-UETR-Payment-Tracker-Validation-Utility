from src.tracker.payment import (
    Payment,
    PaymentStatus,
)


def test_payment_creation():
    payment = Payment(
        uetr="550e8400-e29b-41d4-a716-446655440000",
        amount=10000.0,
        currency="USD",
        origin="SYSTEM_A",
        destination="SYSTEM_B",
    )

    assert payment.status == PaymentStatus.CREATED
    assert payment.amount == 10000.0


def test_payment_status_update():
    payment = Payment(
        uetr="550e8400-e29b-41d4-a716-446655440000",
        amount=10000.0,
        currency="USD",
        origin="SYSTEM_A",
        destination="SYSTEM_B",
    )

    payment.update_status(
        PaymentStatus.PROCESSING
    )

    assert payment.status == PaymentStatus.PROCESSING
    assert payment.updated_at is not None

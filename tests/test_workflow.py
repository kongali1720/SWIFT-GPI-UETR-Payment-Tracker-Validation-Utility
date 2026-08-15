import pytest

from src.tracker.payment import Payment, PaymentStatus
from src.tracker.workflow import PaymentWorkflow


UETR = "550e8400-e29b-41d4-a716-446655440000"


def create_payment() -> Payment:
    return Payment(
        uetr=UETR,
        amount=10000.0,
        currency="USD",
        origin="SYSTEM_A",
        destination="SYSTEM_B",
    )


def test_valid_payment_workflow():
    payment = create_payment()
    workflow = PaymentWorkflow()

    workflow.transition(
        payment,
        PaymentStatus.VALIDATED,
        "Validation successful",
    )

    workflow.transition(
        payment,
        PaymentStatus.PROCESSING,
        "Payment processing started",
    )

    workflow.transition(
        payment,
        PaymentStatus.IN_PROGRESS,
        "Payment is being processed",
    )

    workflow.transition(
        payment,
        PaymentStatus.COMPLETED,
        "Payment completed",
    )

    assert payment.status == PaymentStatus.COMPLETED

    history = workflow.history(UETR)

    assert len(history) == 4
    assert history[-1].new_status == PaymentStatus.COMPLETED


def test_invalid_transition():
    payment = create_payment()
    workflow = PaymentWorkflow()

    with pytest.raises(ValueError):
        workflow.transition(
            payment,
            PaymentStatus.COMPLETED,
        )


def test_failed_payment():
    payment = create_payment()
    workflow = PaymentWorkflow()

    workflow.transition(
        payment,
        PaymentStatus.FAILED,
        "Validation failure",
    )

    assert payment.status == PaymentStatus.FAILED

    history = workflow.history(UETR)

    assert len(history) == 1
    assert history[0].new_status == PaymentStatus.FAILED

import pytest

from src.repository.payment_repository import PaymentRepository
from src.tracker.payment import Payment


UETR = "550e8400-e29b-41d4-a716-446655440000"


def create_payment() -> Payment:
    return Payment(
        uetr=UETR,
        amount=10000.0,
        currency="USD",
        origin="SYSTEM_A",
        destination="SYSTEM_B",
    )


def test_create_and_get_payment():
    repository = PaymentRepository()

    payment = create_payment()

    repository.create(payment)

    stored = repository.get(UETR)

    assert stored is not None
    assert stored.uetr == UETR
    assert stored.amount == 10000.0


def test_duplicate_payment():
    repository = PaymentRepository()

    payment = create_payment()

    repository.create(payment)

    with pytest.raises(ValueError):
        repository.create(payment)


def test_list_and_count():
    repository = PaymentRepository()

    payment = create_payment()

    repository.create(payment)

    assert repository.count() == 1
    assert len(repository.list_all()) == 1


def test_delete_payment():
    repository = PaymentRepository()

    payment = create_payment()

    repository.create(payment)

    assert repository.delete(UETR) is True
    assert repository.get(UETR) is None
    assert repository.count() == 0

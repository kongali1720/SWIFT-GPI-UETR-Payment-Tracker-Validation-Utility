from src.validator.uetr import (
    is_valid_uetr,
    normalize_uetr,
)


def test_valid_uetr():
    uetr = "550e8400-e29b-41d4-a716-446655440000"

    assert is_valid_uetr(uetr) is True


def test_invalid_uetr():
    assert is_valid_uetr("invalid-uetr") is False


def test_normalize_uetr():
    uetr = "550E8400-E29B-41D4-A716-446655440000"

    assert normalize_uetr(uetr) == (
        "550e8400-e29b-41d4-a716-446655440000"
    )

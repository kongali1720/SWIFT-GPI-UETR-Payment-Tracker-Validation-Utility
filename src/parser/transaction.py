from typing import Any

from src.validator.uetr import normalize_uetr


REQUIRED_FIELDS = {
    "uetr",
    "amount",
    "currency",
    "origin",
    "destination",
}


def validate_transaction_payload(
    payload: dict[str, Any]
) -> dict[str, Any]:

    if not isinstance(payload, dict):
        raise TypeError("Transaction payload must be an object")

    missing = REQUIRED_FIELDS - payload.keys()

    if missing:
        raise ValueError(
            f"Missing required fields: {sorted(missing)}"
        )

    normalized = dict(payload)

    normalized["uetr"] = normalize_uetr(
        payload["uetr"]
    )

    if float(payload["amount"]) < 0:
        raise ValueError(
            "Transaction amount cannot be negative"
        )

    normalized["amount"] = float(
        payload["amount"]
    )

    normalized["currency"] = str(
        payload["currency"]
    ).upper()

    return normalized

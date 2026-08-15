import re
import uuid


UETR_PATTERN = re.compile(
    r"^[a-fA-F0-9]{8}-"
    r"[a-fA-F0-9]{4}-"
    r"[a-fA-F0-9]{4}-"
    r"[a-fA-F0-9]{4}-"
    r"[a-fA-F0-9]{12}$"
)


def is_valid_uetr(value: str) -> bool:
    """
    Validate the basic UUID-shaped structure of a UETR.

    This function validates syntax and structure only.
    It does not query SWIFT infrastructure or payment networks.
    """
    if not isinstance(value, str):
        return False

    value = value.strip()

    if not UETR_PATTERN.fullmatch(value):
        return False

    try:
        uuid.UUID(value)
    except ValueError:
        return False

    return True


def normalize_uetr(value: str) -> str:
    """
    Normalize a UETR string for internal processing.
    """
    if not isinstance(value, str):
        raise TypeError("UETR must be a string")

    normalized = value.strip().lower()

    if not is_valid_uetr(normalized):
        raise ValueError("Invalid UETR format")

    return normalized

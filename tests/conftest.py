import os
from pathlib import Path


TEST_DATABASE = Path(
    "data/test_swift_gpi_uetr.db"
)

if TEST_DATABASE.exists():
    TEST_DATABASE.unlink()

os.environ["SWIFT_GPI_UETR_DB"] = str(
    TEST_DATABASE
)

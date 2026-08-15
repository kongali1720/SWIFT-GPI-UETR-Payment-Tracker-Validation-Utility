import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.audit.audit_log import AuditLogger
from src.database.sqlite import SQLiteDatabase
from src.repository.sqlite_audit_repository import SQLiteAuditRepository
from src.repository.sqlite_event_repository import SQLiteEventRepository
from src.repository.sqlite_payment_repository import SQLitePaymentRepository
from src.services.payment_service import PaymentService
from src.tracker.payment import Payment, PaymentStatus
from src.tracker.workflow import PaymentWorkflow
from src.validator.uetr import is_valid_uetr, normalize_uetr


DATABASE_PATH = os.getenv(
    "SWIFT_GPI_UETR_DB",
    "data/swift_gpi_uetr.db",
)


database = SQLiteDatabase(DATABASE_PATH)

payment_repository = SQLitePaymentRepository(
    database
)

event_repository = SQLiteEventRepository(
    database
)

audit_repository = SQLiteAuditRepository(
    database
)

workflow = PaymentWorkflow()

audit = AuditLogger()

payment_service = PaymentService(
    payment_repository=payment_repository,
    workflow=workflow,
    audit_logger=audit,
    event_repository=event_repository,
    audit_repository=audit_repository,
)


app = FastAPI(
    title="SWIFT GPI UETR Payment Tracker",
    description=(
        "Authorized UETR validation, payment tracking, "
        "workflow verification, transaction analysis, "
        "and persistent payment event auditing utility."
    ),
    version="1.1.0",
)


class UETRRequest(BaseModel):
    uetr: str = Field(
        ...,
        description="UETR value to validate",
    )


class PaymentRequest(BaseModel):
    uetr: str
    amount: float = Field(..., ge=0)
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
    )
    origin: str = Field(
        ...,
        min_length=1,
    )
    destination: str = Field(
        ...,
        min_length=1,
    )


class StatusRequest(BaseModel):
    status: PaymentStatus
    reason: str = ""


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "swift-gpi-uetr",
        "version": "1.1.0",
        "environment": "authorized-development-testing",
        "persistence": "sqlite",
    }


@app.post("/api/v1/uetr/validate")
def validate_uetr(request: UETRRequest):
    valid = is_valid_uetr(request.uetr)

    return {
        "uetr": request.uetr,
        "valid": valid,
    }


@app.post("/api/v1/payments", status_code=201)
def create_payment(request: PaymentRequest):
    try:
        uetr = normalize_uetr(request.uetr)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    payment = Payment(
        uetr=uetr,
        amount=request.amount,
        currency=request.currency.upper(),
        origin=request.origin,
        destination=request.destination,
    )

    try:
        payment_service.create_payment(payment)

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail="Payment already exists",
        ) from exc

    return payment.to_dict()


@app.get("/api/v1/payments")
def list_payments():
    payments = payment_service.list_payments()

    return {
        "count": len(payments),
        "payments": [
            payment.to_dict()
            for payment in payments
        ],
    }


@app.get("/api/v1/payments/{uetr}")
def get_payment(uetr: str):
    try:
        normalized = normalize_uetr(uetr)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    payment = payment_service.get_payment(
        normalized
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment.to_dict()


@app.get("/api/v1/payments/{uetr}/events")
def get_payment_events(uetr: str):
    try:
        normalized = normalize_uetr(uetr)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    payment = payment_service.get_payment(
        normalized
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment_service.get_events(
        normalized
    )


@app.post("/api/v1/payments/{uetr}/status")
def update_payment_status(
    uetr: str,
    request: StatusRequest,
):
    try:
        normalized = normalize_uetr(uetr)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    payment = payment_service.get_payment(
        normalized
    )

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    try:
        event = payment_service.update_status(
            payment,
            request.status,
            request.reason,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    return {
        "payment": payment.to_dict(),
        "event": event.to_dict(),
    }

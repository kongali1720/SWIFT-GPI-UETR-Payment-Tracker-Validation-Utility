from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.audit.audit_log import AuditLogger
from src.repository.payment_repository import PaymentRepository
from src.tracker.payment import Payment, PaymentStatus
from src.tracker.workflow import PaymentWorkflow
from src.validator.uetr import is_valid_uetr, normalize_uetr


app = FastAPI(
    title="SWIFT GPI UETR Payment Tracker",
    description=(
        "Authorized UETR validation, payment tracking, "
        "workflow verification, and transaction analysis utility."
    ),
    version="1.0.0",
)


repository = PaymentRepository()
workflow = PaymentWorkflow()
audit = AuditLogger()


class UETRRequest(BaseModel):
    uetr: str = Field(
        ...,
        description="UETR value to validate",
    )


class PaymentRequest(BaseModel):
    uetr: str
    amount: float = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)
    origin: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)


class StatusRequest(BaseModel):
    status: PaymentStatus
    reason: str = ""


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "swift-gpi-uetr",
        "version": "1.0.0",
        "environment": "authorized-development-testing",
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

    if repository.get(uetr):
        raise HTTPException(
            status_code=409,
            detail="Payment already exists",
        )

    payment = Payment(
        uetr=uetr,
        amount=request.amount,
        currency=request.currency.upper(),
        origin=request.origin,
        destination=request.destination,
    )

    repository.create(payment)

    audit.record(
        event_type="PAYMENT_CREATED",
        uetr=uetr,
        message="Payment created",
    )

    return payment.to_dict()


@app.get("/api/v1/payments")
def list_payments():

    return {
        "count": repository.count(),
        "payments": [
            payment.to_dict()
            for payment in repository.list_all()
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

    payment = repository.get(normalized)

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

    payment = repository.get(normalized)

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    workflow_events = [
        event.to_dict()
        for event in workflow.history(normalized)
    ]

    audit_events = [
        event.to_dict()
        for event in audit.get_by_uetr(normalized)
    ]

    return {
        "uetr": normalized,
        "workflow_events": workflow_events,
        "audit_events": audit_events,
    }


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

    payment = repository.get(normalized)

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    try:
        event = workflow.transition(
            payment,
            request.status,
            request.reason,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    repository.update(payment)

    audit.record(
        event_type="STATUS_CHANGED",
        uetr=normalized,
        message=(
            f"{event.previous_status.value} -> "
            f"{event.new_status.value}"
        ),
    )

    return {
        "payment": payment.to_dict(),
        "event": event.to_dict(),
    }

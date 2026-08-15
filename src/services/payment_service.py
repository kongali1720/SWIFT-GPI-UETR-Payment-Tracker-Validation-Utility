from src.audit.audit_log import AuditLogger
from src.repository.payment_repository import PaymentRepository
from src.repository.sqlite_audit_repository import SQLiteAuditRepository
from src.repository.sqlite_event_repository import SQLiteEventRepository
from src.repository.sqlite_payment_repository import SQLitePaymentRepository
from src.tracker.payment import Payment, PaymentStatus
from src.tracker.workflow import PaymentWorkflow


class PaymentService:
    """
    Application service coordinating payment lifecycle operations.

    The service keeps API concerns separate from business logic and
    persistence concerns.
    """

    def __init__(
        self,
        payment_repository,
        workflow: PaymentWorkflow,
        audit_logger: AuditLogger,
        event_repository=None,
        audit_repository=None,
    ):
        self.payment_repository = payment_repository
        self.workflow = workflow
        self.audit_logger = audit_logger
        self.event_repository = event_repository
        self.audit_repository = audit_repository

    def create_payment(
        self,
        payment: Payment,
    ) -> Payment:

        if self.payment_repository.get(payment.uetr):
            raise ValueError(
                f"Payment already exists: {payment.uetr}"
            )

        self.payment_repository.create(payment)

        record = self.audit_logger.record(
            event_type="PAYMENT_CREATED",
            uetr=payment.uetr,
            message="Payment created",
        )

        if self.audit_repository:
            self.audit_repository.save(record)

        return payment

    def get_payment(
        self,
        uetr: str,
    ):
        return self.payment_repository.get(uetr)

    def list_payments(self):
        return self.payment_repository.list_all()

    def update_status(
        self,
        payment: Payment,
        status: PaymentStatus,
        reason: str = "",
    ):
        event = self.workflow.transition(
            payment,
            status,
            reason,
        )

        self.payment_repository.update(payment)

        if self.event_repository:
            self.event_repository.save(event)

        record = self.audit_logger.record(
            event_type="STATUS_CHANGED",
            uetr=payment.uetr,
            message=(
                f"{event.previous_status.value} -> "
                f"{event.new_status.value}"
            ),
        )

        if self.audit_repository:
            self.audit_repository.save(record)

        return event

    def get_events(
        self,
        uetr: str,
    ):
        if self.event_repository:
            workflow_events = (
                self.event_repository.get_by_uetr(uetr)
            )
        else:
            workflow_events = [
                event.to_dict()
                for event in self.workflow.history(uetr)
            ]

        if self.audit_repository:
            audit_events = (
                self.audit_repository.get_by_uetr(uetr)
            )
        else:
            audit_events = [
                event.to_dict()
                for event in self.audit_logger.get_by_uetr(uetr)
            ]

        return {
            "uetr": uetr,
            "workflow_events": workflow_events,
            "audit_events": audit_events,
        }

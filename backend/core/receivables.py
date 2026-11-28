from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, Literal

DEFAULT_AGING_BUCKETS: tuple[tuple[int, int | None], ...] = (
    (1, 30),
    (31, 60),
    (61, 90),
    (91, None),
)

ZERO = Decimal("0")
ONE = Decimal("1")
TWO = Decimal("2")


class ReceivablesValidationError(ValueError):
    """Invalid input for the receivables calculation engine."""


@dataclass(frozen=True)
class InvoiceInput:
    customer_id: str
    invoice_number: str
    invoice_date: date
    due_date: date
    amount: Decimal
    status: Literal["open", "paid", "disputed"]


@dataclass(frozen=True)
class PaymentInput:
    customer_id: str
    invoice_number: str
    payment_date: date
    amount: Decimal


@dataclass(frozen=True)
class InvoiceResult:
    customer_id: str
    invoice_number: str
    balance: Decimal
    credit_balance: Decimal
    disputed: bool
    days_overdue: int | None


@dataclass(frozen=True)
class AgingResult:
    report_date: date
    bucket_definitions: tuple[tuple[int, int | None], ...]
    buckets: dict[str, Decimal]
    disputed_subtotal: dict[str, Decimal]


@dataclass(frozen=True)
class DSOResult:
    dso: Decimal | None
    average_ar: Decimal
    credit_sales: Decimal
    days_in_period: int
    opening_ar_assumed: bool


@dataclass(frozen=True)
class ReceivablesResult:
    report_date: date
    invoice_results: tuple[InvoiceResult, ...]
    total_outstanding: Decimal
    overdue_amount: Decimal
    overdue_ratio: Decimal | None
    disputed_outstanding: Decimal
    aging: AgingResult
    adbt: Decimal | None
    dso: DSOResult


def _validate_amount(amount: Decimal, label: str) -> None:
    if not isinstance(amount, Decimal) or not amount.is_finite():
        raise ReceivablesValidationError(f"{label} must be a finite Decimal")
    if amount.as_tuple().exponent < -2:
        raise ReceivablesValidationError(
            f"{label} must not have more than two fractional digits"
        )
    if amount <= ZERO:
        raise ReceivablesValidationError(f"{label} must be greater than zero")


VALID_STATUSES: tuple[str, ...] = ("open", "paid", "disputed")


def _validate_non_empty_string(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReceivablesValidationError(f"{label} must be a non-empty string")


def _validate_status(status: str, label: str) -> None:
    if status not in VALID_STATUSES:
        raise ReceivablesValidationError(
            f"{label} must be one of {', '.join(VALID_STATUSES)}"
        )


def _bucket_label(bucket: tuple[int, int | None]) -> str:
    lower, upper = bucket
    if upper is None:
        return f"Over {lower - 1}"
    return f"{lower}-{upper}"


def _validated_buckets(
    buckets: tuple[tuple[int, int | None], ...] | None,
) -> tuple[tuple[int, int | None], ...]:
    selected = DEFAULT_AGING_BUCKETS if buckets is None else tuple(buckets)
    if not selected:
        raise ReceivablesValidationError("At least one overdue bucket is required")

    expected_lower = 1
    for index, bucket in enumerate(selected):
        if not isinstance(bucket, tuple) or len(bucket) != 2:
            raise ReceivablesValidationError(
                "Each overdue bucket must be a (lower_day, upper_day) pair"
            )
        lower, upper = bucket
        if (
            isinstance(lower, bool)
            or not isinstance(lower, int)
            or lower != expected_lower
        ):
            raise ReceivablesValidationError(
                "Overdue buckets must be ordered, contiguous, and start at day 1"
            )
        if upper is not None and (
            isinstance(upper, bool) or not isinstance(upper, int) or upper < lower
        ):
            raise ReceivablesValidationError(
                "An overdue bucket upper day must be at least its lower day"
            )
        if upper is None:
            if index != len(selected) - 1:
                raise ReceivablesValidationError(
                    "Only the final overdue bucket may be open-ended"
                )
        else:
            expected_lower = upper + 1

    if selected[-1][1] is not None:
        raise ReceivablesValidationError("The final overdue bucket must be open-ended")
    return selected


def calculate_receivables(
    *,
    invoices: Iterable[InvoiceInput],
    payments: Iterable[PaymentInput],
    report_date: date,
    period_start: date,
    period_end: date,
    opening_ar: Decimal | None,
    aging_buckets: tuple[tuple[int, int | None], ...] | None = None,
) -> ReceivablesResult:
    """Calculate receivables for one tenant's already-scoped input records."""
    if period_start > period_end:
        raise ReceivablesValidationError("period_start must not be after period_end")
    if not period_start <= report_date <= period_end:
        raise ReceivablesValidationError(
            "report_date must be within the inclusive reporting period"
        )

    selected_buckets = _validated_buckets(aging_buckets)
    eligible_invoices = [
        invoice for invoice in invoices if invoice.invoice_date <= report_date
    ]
    eligible_payments = [
        payment for payment in payments if payment.payment_date <= report_date
    ]

    invoices_by_key: dict[tuple[str, str], InvoiceInput] = {}
    seen_invoice_numbers: set[str] = set()
    for invoice in eligible_invoices:
        _validate_non_empty_string(invoice.customer_id, "customer_id")
        _validate_non_empty_string(invoice.invoice_number, "invoice number")
        _validate_status(invoice.status, "invoice status")

        if invoice.invoice_number in seen_invoice_numbers:
            raise ReceivablesValidationError(
                f"Duplicate eligible invoice number: {invoice.invoice_number}"
            )
        seen_invoice_numbers.add(invoice.invoice_number)
        invoices_by_key[(invoice.customer_id, invoice.invoice_number)] = invoice

        _validate_amount(invoice.amount, "invoice amount")
        if invoice.due_date < invoice.invoice_date:
            raise ReceivablesValidationError(
                f"Invoice {invoice.invoice_number} due date cannot precede its invoice date"
            )

    payments_by_key: dict[tuple[str, str], list[PaymentInput]] = defaultdict(list)
    for payment in eligible_payments:
        _validate_amount(payment.amount, "payment amount")
        _validate_non_empty_string(payment.customer_id, "customer_id")
        _validate_non_empty_string(payment.invoice_number, "invoice number")
        key = (payment.customer_id, payment.invoice_number)
        matching_invoice = invoices_by_key.get(key)
        # Payments whose invoice_number matches no eligible invoice (an orphan
        # number, or a number that exists only on a future-dated invoice) have
        # already been amount-validated above and are then ignored: they affect
        # no balance, bucket, overdue total, credit balance, or ADBT figure.
        if matching_invoice is None:
            continue
        if payment.payment_date < matching_invoice.invoice_date:
            raise ReceivablesValidationError(
                f"Payment for invoice {payment.invoice_number} cannot precede its invoice date"
            )
        payments_by_key[key].append(payment)

    bucket_labels = ("Current",) + tuple(
        _bucket_label(bucket) for bucket in selected_buckets
    )
    bucket_totals = {label: ZERO for label in bucket_labels}
    disputed_totals = {label: ZERO for label in bucket_labels}
    invoice_results: list[InvoiceResult] = []
    total_outstanding = ZERO
    overdue_amount = ZERO
    disputed_outstanding = ZERO
    adbt_differences: list[Decimal] = []
    closing_ar = ZERO

    for invoice in eligible_invoices:
        key = (invoice.customer_id, invoice.invoice_number)
        invoice_payments = payments_by_key.get(key, [])
        paid_amount = sum((item.amount for item in invoice_payments), ZERO)
        balance = max(invoice.amount - paid_amount, ZERO)
        credit_balance = max(paid_amount - invoice.amount, ZERO)
        disputed = invoice.status == "disputed"
        total_outstanding += balance
        closing_ar += balance
        if disputed:
            disputed_outstanding += balance

        days_overdue: int | None = None
        if invoice.due_date < report_date:
            days_overdue = (report_date - invoice.due_date).days
        if balance > ZERO:
            if days_overdue is None:
                bucket_label = "Current"
            else:
                bucket_label = next(
                    _bucket_label(bucket)
                    for bucket in selected_buckets
                    if bucket[0] <= days_overdue
                    and (bucket[1] is None or days_overdue <= bucket[1])
                )
                overdue_amount += balance
            bucket_totals[bucket_label] += balance
            if disputed:
                disputed_totals[bucket_label] += balance

        invoice_results.append(
            InvoiceResult(
                customer_id=invoice.customer_id,
                invoice_number=invoice.invoice_number,
                balance=balance,
                credit_balance=credit_balance,
                disputed=disputed,
                days_overdue=days_overdue,
            )
        )

        daily_payments: dict[date, Decimal] = defaultdict(lambda: ZERO)
        for item in invoice_payments:
            daily_payments[item.payment_date] += item.amount
        cumulative_payments = ZERO
        final_settlement_date: date | None = None
        for payment_date in sorted(daily_payments):
            cumulative_payments += daily_payments[payment_date]
            if cumulative_payments >= invoice.amount:
                final_settlement_date = payment_date
                break
        if (
            final_settlement_date is not None
            and period_start <= final_settlement_date <= report_date
        ):
            adbt_differences.append(
                Decimal((final_settlement_date - invoice.due_date).days)
            )

    overdue_ratio = (
        overdue_amount / total_outstanding if total_outstanding != ZERO else None
    )
    adbt = (
        sum(adbt_differences, ZERO) / Decimal(len(adbt_differences))
        if adbt_differences
        else None
    )

    effective_period_end = report_date
    days_in_period = (effective_period_end - period_start).days + 1
    credit_sales = sum(
        (
            invoice.amount
            for invoice in eligible_invoices
            if period_start <= invoice.invoice_date <= effective_period_end
        ),
        ZERO,
    )
    opening_ar_assumed = opening_ar is None
    effective_opening_ar = ZERO if opening_ar is None else opening_ar
    if (
        not isinstance(effective_opening_ar, Decimal)
        or not effective_opening_ar.is_finite()
    ):
        raise ReceivablesValidationError("opening_ar must be a finite Decimal or None")
    if effective_opening_ar < ZERO:
        raise ReceivablesValidationError("opening_ar must not be negative")
    average_ar = (effective_opening_ar + closing_ar) / TWO
    dso = (
        (average_ar / credit_sales) * Decimal(days_in_period)
        if credit_sales != ZERO
        else None
    )

    return ReceivablesResult(
        report_date=report_date,
        invoice_results=tuple(invoice_results),
        total_outstanding=total_outstanding,
        overdue_amount=overdue_amount,
        overdue_ratio=overdue_ratio,
        disputed_outstanding=disputed_outstanding,
        aging=AgingResult(
            report_date=report_date,
            bucket_definitions=selected_buckets,
            buckets=bucket_totals,
            disputed_subtotal=disputed_totals,
        ),
        adbt=adbt,
        dso=DSOResult(
            dso=dso,
            average_ar=average_ar,
            credit_sales=credit_sales,
            days_in_period=days_in_period,
            opening_ar_assumed=opening_ar_assumed,
        ),
    )

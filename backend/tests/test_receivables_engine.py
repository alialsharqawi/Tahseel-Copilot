from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.receivables import (
    DEFAULT_AGING_BUCKETS,
    InvoiceInput,
    PaymentInput,
    ReceivablesValidationError,
    calculate_receivables,
)


REPORT_DATE = date(2026, 11, 26)


def invoice(
    *,
    number: str,
    customer_id: str = "customer-1",
    invoice_date: date = date(2026, 1, 1),
    due_date: date = date(2026, 2, 1),
    amount: Decimal = Decimal("100.00"),
    status: str = "open",
) -> InvoiceInput:
    return InvoiceInput(
        customer_id=customer_id,
        invoice_number=number,
        invoice_date=invoice_date,
        due_date=due_date,
        amount=amount,
        status=status,
    )


def payment(
    *,
    invoice_number: str,
    amount: Decimal,
    customer_id: str = "customer-1",
    payment_date: date = REPORT_DATE,
) -> PaymentInput:
    return PaymentInput(
        customer_id=customer_id,
        invoice_number=invoice_number,
        payment_date=payment_date,
        amount=amount,
    )


def calculate(
    invoices: list[InvoiceInput],
    payments: list[PaymentInput] | None = None,
    *,
    report_date: date = REPORT_DATE,
    period_start: date = date(2026, 1, 1),
    period_end: date = date(2026, 11, 30),
    opening_ar: Decimal | None = Decimal("0"),
    aging_buckets: tuple[tuple[int, int | None], ...] | None = None,
):
    return calculate_receivables(
        invoices=invoices,
        payments=payments or [],
        report_date=report_date,
        period_start=period_start,
        period_end=period_end,
        opening_ar=opening_ar,
        aging_buckets=aging_buckets,
    )


def test_future_records_are_ignored_before_validation() -> None:
    future_invoice = invoice(
        number="FUTURE",
        invoice_date=date(2026, 12, 1),
        due_date=date(2026, 11, 30),
        amount=Decimal("-10"),
    )
    result = calculate(
        [future_invoice],
        [
            payment(
                invoice_number="FUTURE",
                amount=Decimal("-5"),
                payment_date=date(2026, 12, 2),
            )
        ],
    )

    assert result.total_outstanding == Decimal("0")
    assert result.overdue_ratio is None


def test_future_duplicate_numbers_are_ignored() -> None:
    future_date = date(2026, 12, 1)
    result = calculate(
        [
            invoice(
                number="DUPLICATE",
                invoice_date=future_date,
                due_date=future_date,
                amount=Decimal("100"),
            ),
            invoice(
                number="DUPLICATE",
                invoice_date=future_date,
                due_date=future_date,
                amount=Decimal("-100"),
            ),
        ]
    )

    assert result.total_outstanding == Decimal("0")


def test_report_date_controls_eligible_payments() -> None:
    inv = invoice(number="INV-1", amount=Decimal("100"))
    result = calculate(
        [inv],
        [
            payment(
                invoice_number="INV-1",
                amount=Decimal("40"),
                payment_date=date(2026, 11, 26),
            ),
            payment(
                invoice_number="INV-1",
                amount=Decimal("70"),
                payment_date=date(2026, 11, 27),
            ),
        ],
    )

    item = result.invoice_results[0]
    assert item.balance == Decimal("60")
    assert item.credit_balance == Decimal("0")


def test_partial_and_full_settlement_use_payment_records() -> None:
    invoices = [
        invoice(number="PARTIAL", amount=Decimal("100")),
        invoice(number="PAID", amount=Decimal("80")),
    ]
    result = calculate(
        invoices,
        [
            payment(
                invoice_number="PARTIAL",
                amount=Decimal("25"),
            ),
            payment(
                invoice_number="PAID",
                amount=Decimal("30"),
            ),
            payment(
                invoice_number="PAID",
                amount=Decimal("50"),
            ),
        ],
    )

    by_number = {item.invoice_number: item for item in result.invoice_results}
    assert by_number["PARTIAL"].balance == Decimal("75")
    assert by_number["PAID"].balance == Decimal("0")


@pytest.mark.parametrize(
    ("status", "expected_balance"),
    [
        ("paid", Decimal("100")),
        ("open", Decimal("0")),
        ("disputed", Decimal("100")),
    ],
)
def test_invoice_status_does_not_override_payment_arithmetic(
    status: str,
    expected_balance: Decimal,
) -> None:
    inv = invoice(number="STATUS", amount=Decimal("100"), status=status)
    payments = (
        []
        if status in {"paid", "disputed"}
        else [payment(invoice_number="STATUS", amount=Decimal("100"))]
    )
    result = calculate([inv], payments)

    assert result.invoice_results[0].balance == expected_balance


def test_overpayment_tracks_credit_without_offsetting_or_receivables() -> None:
    invoices = [
        invoice(
            number="OVER",
            due_date=date(2026, 10, 1),
            amount=Decimal("80"),
        ),
        invoice(
            number="OTHER",
            due_date=date(2026, 10, 1),
            amount=Decimal("50"),
        ),
    ]
    result = calculate(
        invoices,
        [
            payment(invoice_number="OVER", amount=Decimal("100")),
        ],
    )

    by_number = {item.invoice_number: item for item in result.invoice_results}
    assert by_number["OVER"].balance == Decimal("0")
    assert by_number["OVER"].credit_balance == Decimal("20")
    assert by_number["OTHER"].balance == Decimal("50")
    assert result.total_outstanding == Decimal("50")
    assert result.overdue_amount == Decimal("50")
    assert result.overdue_ratio == Decimal("1")
    assert sum(result.aging.buckets.values()) == Decimal("50")
    assert result.dso.average_ar == Decimal("25")


def test_payments_are_attributed_by_customer_and_invoice_number() -> None:
    invoices = [
        invoice(number="INV-1", customer_id="customer-1"),
        invoice(number="INV-2", customer_id="customer-1"),
        invoice(number="INV-3", customer_id="customer-2"),
    ]
    result = calculate(
        invoices,
        [
            payment(
                invoice_number="INV-1",
                customer_id="customer-1",
                amount=Decimal("40"),
            ),
            payment(
                invoice_number="INV-2",
                customer_id="customer-1",
                amount=Decimal("25"),
            ),
            payment(
                invoice_number="INV-3",
                customer_id="customer-2",
                amount=Decimal("70"),
            ),
            payment(
                invoice_number="INV-1",
                customer_id="customer-2",
                amount=Decimal("10"),
            ),
        ],
    )

    by_key = {
        (item.customer_id, item.invoice_number): item for item in result.invoice_results
    }
    assert by_key[("customer-1", "INV-1")].balance == Decimal("60")
    assert by_key[("customer-1", "INV-2")].balance == Decimal("75")
    assert by_key[("customer-2", "INV-3")].balance == Decimal("30")


@pytest.mark.parametrize(
    ("due_date", "expected_bucket"),
    [
        (date(2026, 11, 26), "Current"),
        (date(2026, 11, 27), "Current"),
        (date(2026, 10, 27), "1-30"),
        (date(2026, 10, 26), "31-60"),
        (date(2026, 9, 27), "31-60"),
        (date(2026, 9, 26), "61-90"),
        (date(2026, 8, 28), "61-90"),
        (date(2026, 8, 27), "Over 90"),
    ],
)
def test_aging_bucket_boundaries(
    due_date: date,
    expected_bucket: str,
) -> None:
    result = calculate([invoice(number="AGING", due_date=due_date)])

    if expected_bucket == "Current":
        assert result.aging.buckets["Current"] == Decimal("100")
    else:
        assert result.aging.buckets[expected_bucket] == Decimal("100")


def test_default_aging_buckets() -> None:
    result = calculate([invoice(number="AGING")])

    assert result.aging.bucket_definitions == DEFAULT_AGING_BUCKETS
    assert tuple(result.aging.buckets) == (
        "Current",
        "1-30",
        "31-60",
        "61-90",
        "Over 90",
    )


def test_valid_custom_aging_buckets_are_accepted_and_used() -> None:
    custom_buckets = ((1, 15), (16, 30), (31, None))
    result = calculate(
        [
            invoice(
                number="CUSTOM",
                due_date=date(2026, 11, 11),
                amount=Decimal("100"),
            )
        ],
        aging_buckets=custom_buckets,
    )

    assert result.aging.bucket_definitions == custom_buckets
    assert result.aging.buckets["1-15"] == Decimal("100")
    assert sum(
        amount for bucket, amount in result.aging.buckets.items() if bucket != "Current"
    ) == Decimal("100")


@pytest.mark.parametrize(
    "buckets",
    [
        ((1, 30), (32, 60), (61, None)),
        ((1, 30), (20, 60), (61, None)),
        ((2, 30), (31, 60), (61, None)),
        ((1, 30), (31, 60), (61, 90)),
    ],
)
def test_invalid_custom_aging_buckets_raise(
    buckets: tuple[tuple[int, int | None], ...],
) -> None:
    with pytest.raises(ReceivablesValidationError):
        calculate(
            [invoice(number="AGING")],
            aging_buckets=buckets,
        )


def test_disputed_balance_is_flagged_in_buckets_and_totals() -> None:
    result = calculate(
        [
            invoice(
                number="DISPUTED",
                due_date=date(2026, 8, 1),
                amount=Decimal("100"),
                status="disputed",
            )
        ]
    )

    assert sum(result.aging.buckets.values()) == Decimal("100")
    assert sum(result.aging.disputed_subtotal.values()) == Decimal("100")
    assert result.disputed_outstanding == Decimal("100")
    assert result.overdue_amount == Decimal("100")
    assert result.overdue_ratio == Decimal("1")


def test_disputed_balance_is_included_in_dso_closing_ar() -> None:
    result = calculate(
        [
            invoice(
                number="DISPUTED",
                invoice_date=date(2026, 1, 1),
                due_date=date(2026, 8, 1),
                amount=Decimal("100"),
                status="disputed",
            )
        ],
        report_date=date(2026, 11, 26),
        period_start=date(2026, 1, 1),
        period_end=date(2026, 11, 30),
        opening_ar=Decimal("0"),
    )

    expected_average_ar = Decimal("100") / Decimal("2")
    expected_dso = (expected_average_ar / Decimal("100")) * Decimal(
        result.dso.days_in_period
    )
    assert result.dso.average_ar == expected_average_ar
    assert result.dso.credit_sales == Decimal("100")
    assert result.dso.dso == expected_dso


def test_overdue_ratio_is_fraction_and_is_null_at_zero_outstanding() -> None:
    overdue = calculate(
        [
            invoice(
                number="OVERDUE",
                due_date=date(2026, 10, 1),
                amount=Decimal("25"),
            ),
            invoice(
                number="CURRENT",
                due_date=date(2026, 12, 1),
                amount=Decimal("75"),
            ),
        ]
    )
    assert overdue.overdue_ratio == Decimal("0.25")

    empty = calculate(
        [invoice(number="PAID", amount=Decimal("100"))],
        [payment(invoice_number="PAID", amount=Decimal("100"))],
    )
    assert empty.overdue_ratio is None


def test_adbt_settlement_uses_same_day_totals_and_ignores_later_excess() -> None:
    result = calculate(
        [
            invoice(
                number="ADBT",
                due_date=date(2026, 6, 1),
                amount=Decimal("100"),
            )
        ],
        [
            payment(
                invoice_number="ADBT",
                amount=Decimal("40"),
                payment_date=date(2026, 6, 2),
            ),
            payment(
                invoice_number="ADBT",
                amount=Decimal("60"),
                payment_date=date(2026, 6, 2),
            ),
            payment(
                invoice_number="ADBT",
                amount=Decimal("200"),
                payment_date=date(2026, 6, 20),
            ),
        ],
        report_date=date(2026, 11, 26),
        period_start=date(2026, 1, 1),
        period_end=date(2026, 11, 30),
    )

    assert result.adbt == Decimal("1")


def test_adbt_is_average_across_eligible_fully_settled_invoices() -> None:
    result = calculate(
        [
            invoice(
                number="EARLY",
                due_date=date(2026, 6, 10),
                amount=Decimal("100"),
            ),
            invoice(
                number="LATE",
                due_date=date(2026, 6, 10),
                amount=Decimal("100"),
            ),
            invoice(
                number="PARTIAL",
                due_date=date(2026, 6, 10),
                amount=Decimal("100"),
            ),
        ],
        [
            payment(
                invoice_number="EARLY",
                amount=Decimal("100"),
                payment_date=date(2026, 6, 5),
            ),
            payment(
                invoice_number="LATE",
                amount=Decimal("100"),
                payment_date=date(2026, 6, 14),
            ),
            payment(
                invoice_number="PARTIAL",
                amount=Decimal("25"),
                payment_date=date(2026, 6, 12),
            ),
        ],
    )

    assert result.adbt == Decimal("-0.5")


def test_adbt_returns_null_without_eligible_fully_settled_invoice() -> None:
    result = calculate(
        [invoice(number="PARTIAL", amount=Decimal("100"))],
        [payment(invoice_number="PARTIAL", amount=Decimal("99"))],
    )

    assert result.adbt is None


def test_dso_uses_complete_formula_for_full_period() -> None:
    result = calculate(
        [
            invoice(
                number="SALE",
                invoice_date=date(2026, 11, 15),
                due_date=date(2026, 11, 30),
                amount=Decimal("200"),
            )
        ],
        report_date=date(2026, 11, 30),
        period_start=date(2026, 11, 1),
        period_end=date(2026, 11, 30),
        opening_ar=Decimal("100"),
    )

    average_ar = (Decimal("100") + Decimal("200")) / Decimal("2")
    expected = (average_ar / Decimal("200")) * Decimal("30")
    assert result.dso.average_ar == average_ar
    assert result.dso.credit_sales == Decimal("200")
    assert result.dso.days_in_period == 30
    assert result.dso.dso == expected


def test_dso_truncated_period_ends_inclusively_at_report_date() -> None:
    result = calculate(
        [
            invoice(
                number="SALE",
                invoice_date=date(2026, 11, 5),
                due_date=date(2026, 11, 10),
                amount=Decimal("200"),
            )
        ],
        report_date=date(2026, 11, 10),
        period_start=date(2026, 11, 1),
        period_end=date(2026, 11, 30),
        opening_ar=Decimal("100"),
    )

    closing_ar = Decimal("200")
    average_ar = (Decimal("100") + closing_ar) / Decimal("2")
    days_in_period = 10
    expected = (average_ar / Decimal("200")) * Decimal(days_in_period)

    assert result.dso.days_in_period == days_in_period
    assert result.dso.credit_sales == Decimal("200")
    assert result.dso.dso == expected


def test_dso_missing_opening_ar_is_assumed_but_explicit_zero_is_not() -> None:
    inv = [
        invoice(
            number="SALE",
            invoice_date=date(2026, 11, 15),
            due_date=date(2026, 11, 15),
            amount=Decimal("100"),
        )
    ]
    missing = calculate(
        inv,
        report_date=date(2026, 11, 30),
        opening_ar=None,
    )
    explicit = calculate(
        inv,
        report_date=date(2026, 11, 30),
        opening_ar=Decimal("0"),
    )

    assert missing.dso.opening_ar_assumed is True
    assert explicit.dso.opening_ar_assumed is False


def test_negative_opening_ar_raises() -> None:
    inv = [
        invoice(
            number="SALE",
            invoice_date=date(2026, 11, 15),
            due_date=date(2026, 11, 15),
            amount=Decimal("100"),
        )
    ]
    with pytest.raises(ReceivablesValidationError):
        calculate(
            inv,
            report_date=date(2026, 11, 30),
            opening_ar=Decimal("-10"),
        )


def test_explicit_zero_opening_ar_is_accepted_and_not_flagged() -> None:
    inv = [
        invoice(
            number="SALE",
            invoice_date=date(2026, 11, 15),
            due_date=date(2026, 11, 15),
            amount=Decimal("100"),
        )
    ]
    explicit = calculate(
        inv,
        report_date=date(2026, 11, 30),
        opening_ar=Decimal("0"),
    )
    assert explicit.dso.opening_ar_assumed is False
    assert explicit.dso.average_ar == Decimal("50")


def test_dso_zero_credit_sales_returns_null() -> None:
    result = calculate(
        [],
        report_date=date(2026, 11, 30),
        period_start=date(2026, 11, 1),
        period_end=date(2026, 11, 30),
    )

    assert result.dso.credit_sales == Decimal("0")
    assert result.dso.dso is None


@pytest.mark.parametrize(
    ("amount", "is_invoice"),
    [
        (Decimal("0"), True),
        (Decimal("-1"), True),
        (Decimal("0"), False),
        (Decimal("-1"), False),
    ],
)
def test_zero_or_negative_amounts_raise(
    amount: Decimal,
    is_invoice: bool,
) -> None:
    if is_invoice:
        with pytest.raises(ReceivablesValidationError):
            calculate([invoice(number="BAD", amount=amount)])
    else:
        with pytest.raises(ReceivablesValidationError):
            calculate(
                [invoice(number="BAD", amount=Decimal("100"))],
                [payment(invoice_number="BAD", amount=amount)],
            )


@pytest.mark.parametrize(
    ("amount", "is_invoice"),
    [
        (Decimal("1.230"), True),
        (Decimal("1.230"), False),
    ],
)
def test_raw_amount_over_precision_raises(
    amount: Decimal,
    is_invoice: bool,
) -> None:
    if is_invoice:
        with pytest.raises(ReceivablesValidationError):
            calculate([invoice(number="PRECISION", amount=amount)])
    else:
        with pytest.raises(ReceivablesValidationError):
            calculate(
                [invoice(number="PRECISION", amount=Decimal("100"))],
                [payment(invoice_number="PRECISION", amount=amount)],
            )


def test_payment_before_invoice_date_raises() -> None:
    inv = invoice(
        number="DATE",
        invoice_date=date(2026, 5, 10),
        due_date=date(2026, 6, 10),
    )

    with pytest.raises(ReceivablesValidationError):
        calculate(
            [inv],
            [
                payment(
                    invoice_number="DATE",
                    amount=Decimal("10"),
                    payment_date=date(2026, 5, 9),
                )
            ],
        )


def test_due_date_before_invoice_date_raises() -> None:
    inv = invoice(
        number="DATE",
        invoice_date=date(2026, 5, 10),
        due_date=date(2026, 5, 9),
    )

    with pytest.raises(ReceivablesValidationError):
        calculate([inv])


def test_due_date_may_equal_invoice_date() -> None:
    inv = invoice(
        number="DATE",
        invoice_date=date(2026, 5, 10),
        due_date=date(2026, 5, 10),
    )

    result = calculate([inv])
    assert result.invoice_results[0].balance == Decimal("100")


def test_duplicate_eligible_invoice_numbers_raise() -> None:
    with pytest.raises(ReceivablesValidationError):
        calculate(
            [
                invoice(number="DUPLICATE"),
                invoice(number="DUPLICATE"),
            ]
        )


def test_invalid_invoice_status_raises() -> None:
    with pytest.raises(ReceivablesValidationError):
        calculate(
            [invoice(number="BAD", status="overdue")],
        )


def test_blank_customer_id_raises() -> None:
    with pytest.raises(ReceivablesValidationError):
        calculate(
            [invoice(number="BAD", customer_id="")],
        )


def test_blank_invoice_number_raises() -> None:
    with pytest.raises(ReceivablesValidationError):
        calculate(
            [invoice(number="")],
        )


def test_future_dated_invalid_record_is_ignored_not_validated() -> None:
    future_date = date(2026, 12, 1)
    result = calculate(
        [
            invoice(
                number="FUTURE-BAD",
                invoice_date=future_date,
                due_date=future_date,
                amount=Decimal("100"),
                status="not-a-status",
                customer_id="",
            ),
        ]
    )
    assert result.total_outstanding == Decimal("0")


def test_orphan_payment_is_amount_validated_and_ignored() -> None:
    inv = invoice(number="REAL", amount=Decimal("100"))
    result = calculate(
        [inv],
        [
            payment(
                invoice_number="NO-MATCH",
                amount=Decimal("40"),
                customer_id="customer-1",
            ),
        ],
    )
    assert result.total_outstanding == Decimal("100")
    assert result.overdue_amount == Decimal("100")
    assert result.invoice_results[0].balance == Decimal("100")
    assert result.invoice_results[0].credit_balance == Decimal("0")


def test_orphan_payment_invalid_amount_raises() -> None:
    inv = invoice(number="REAL", amount=Decimal("100"))
    with pytest.raises(ReceivablesValidationError):
        calculate(
            [inv],
            [
                payment(
                    invoice_number="NO-MATCH",
                    amount=Decimal("-5"),
                    customer_id="customer-1",
                ),
            ],
        )


def test_payment_for_future_invoice_is_ignored() -> None:
    future_date = date(2026, 12, 1)
    future_inv = invoice(
        number="FUTURE-INV",
        invoice_date=future_date,
        due_date=future_date,
        amount=Decimal("100"),
    )
    real_inv = invoice(number="REAL", amount=Decimal("100"))
    result = calculate(
        [future_inv, real_inv],
        [
            payment(
                invoice_number="FUTURE-INV",
                amount=Decimal("40"),
                customer_id="customer-1",
                payment_date=date(2026, 11, 26),
            ),
        ],
    )
    assert result.total_outstanding == Decimal("100")
    assert result.overdue_amount == Decimal("100")
    assert result.invoice_results[0].invoice_number == "REAL"


@pytest.mark.parametrize(
    ("period_start", "period_end", "report_date"),
    [
        (date(2026, 11, 2), date(2026, 11, 1), date(2026, 11, 1)),
        (date(2026, 11, 1), date(2026, 11, 30), date(2026, 10, 31)),
        (date(2026, 11, 1), date(2026, 11, 30), date(2026, 12, 1)),
    ],
)
def test_invalid_period_or_report_date_raise(
    period_start: date,
    period_end: date,
    report_date: date,
) -> None:
    with pytest.raises(ReceivablesValidationError):
        calculate(
            [],
            report_date=report_date,
            period_start=period_start,
            period_end=period_end,
        )


def test_one_day_period_is_valid() -> None:
    result = calculate(
        [],
        report_date=date(2026, 11, 30),
        period_start=date(2026, 11, 30),
        period_end=date(2026, 11, 30),
    )

    assert result.dso.days_in_period == 1

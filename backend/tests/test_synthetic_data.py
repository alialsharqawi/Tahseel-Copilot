from __future__ import annotations

import json
import uuid
from decimal import Decimal
from pathlib import Path

import pytest

from scripts.generate_synthetic_data import (
    DEFAULT_REFERENCE_DATE,
    DEFAULT_SEED,
    DEFAULT_TENANT_ID,
    generate_synthetic_data,
    validate_synthetic_data,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT_DIR / "data" / "demo" / "receivables.json"


def test_default_fixture_has_expected_records_and_distributions() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture["metadata"]["synthetic"] is True
    assert fixture["metadata"]["seed"] == DEFAULT_SEED
    assert fixture["metadata"]["reference_date"] == DEFAULT_REFERENCE_DATE.isoformat()
    assert len(fixture["customers"]) == 120
    assert len(fixture["invoices"]) == 1500
    assert len(fixture["payments"]) == 2500
    assert len(fixture["promises_to_pay"]) == 30

    archetypes = {customer["archetype"] for customer in fixture["customers"]}
    assert archetypes == {"reliable", "late", "chronic_late"}
    assert (
        sum(customer["archetype"] == "reliable" for customer in fixture["customers"])
        == 72
    )
    assert (
        sum(customer["archetype"] == "late" for customer in fixture["customers"]) == 30
    )
    assert (
        sum(
            customer["archetype"] == "chronic_late" for customer in fixture["customers"]
        )
        == 18
    )

    invoice_statuses = {
        status: sum(invoice["status"] == status for invoice in fixture["invoices"])
        for status in ("open", "paid", "disputed")
    }
    assert invoice_statuses == {"open": 375, "paid": 975, "disputed": 150}
    partially_paid_open = [
        invoice
        for invoice in fixture["invoices"]
        if invoice["status"] == "open" and Decimal(invoice["paid_amount"]) > 0
    ]
    assert len(partially_paid_open) == 300

    payments_per_paid_invoice = {
        invoice["id"]: sum(
            payment["invoice_id"] == invoice["id"] for payment in fixture["payments"]
        )
        for invoice in fixture["invoices"]
        if invoice["status"] == "paid"
    }
    assert sum(count == 1 for count in payments_per_paid_invoice.values()) == 50
    assert sum(count == 2 for count in payments_per_paid_invoice.values()) == 925
    assert 50 + 925 * 2 + len(partially_paid_open) * 2 == len(fixture["payments"])
    assert len(fixture["payments"]) == 2500

    promise_statuses = {
        status: sum(
            promise["status"] == status for promise in fixture["promises_to_pay"]
        )
        for status in ("pending", "kept", "broken")
    }
    assert promise_statuses == {"pending": 4, "kept": 15, "broken": 11}

    strategic_count = sum(
        customer["tier"] == "strategic" for customer in fixture["customers"]
    )
    assert strategic_count == 24


def test_relationships_payment_totals_and_statuses_are_consistent() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    validate_synthetic_data(fixture)

    customer_ids = {customer["id"] for customer in fixture["customers"]}
    invoice_ids = {invoice["id"] for invoice in fixture["invoices"]}
    payment_totals = {invoice_id: Decimal("0.00") for invoice_id in invoice_ids}

    for payment in fixture["payments"]:
        assert payment["customer_id"] in customer_ids
        assert payment["invoice_id"] in invoice_ids
        payment_totals[payment["invoice_id"]] += Decimal(payment["amount"])

    for invoice in fixture["invoices"]:
        assert payment_totals[invoice["id"]] == Decimal(invoice["paid_amount"])
        amount = Decimal(invoice["amount"])
        paid = payment_totals[invoice["id"]]
        if invoice["status"] == "paid":
            assert paid == amount
        else:
            assert paid < amount
        if invoice["status"] == "disputed":
            assert invoice["dispute_reason"]
            assert invoice["disputed_by"]

    for promise in fixture["promises_to_pay"]:
        assert promise["customer_id"] in customer_ids
        assert promise["invoice_id"] in invoice_ids
        assert promise["status"] in ("pending", "kept", "broken")


def test_generator_is_reproducible_for_default_inputs() -> None:
    first = generate_synthetic_data(
        seed=DEFAULT_SEED,
        reference_date=DEFAULT_REFERENCE_DATE,
        tenant_id=DEFAULT_TENANT_ID,
    )
    second = generate_synthetic_data(
        seed=DEFAULT_SEED,
        reference_date=DEFAULT_REFERENCE_DATE,
        tenant_id=DEFAULT_TENANT_ID,
    )

    assert first == second


def test_seed_reference_date_and_tenant_id_are_configurable() -> None:
    first = generate_synthetic_data(
        seed=17,
        reference_date=DEFAULT_REFERENCE_DATE,
        tenant_id=uuid.UUID("22222222-2222-4222-8222-222222222222"),
    )
    second = generate_synthetic_data(
        seed=18,
        reference_date=DEFAULT_REFERENCE_DATE,
        tenant_id=uuid.UUID("22222222-2222-4222-8222-222222222222"),
    )

    assert len(first["customers"]) == 120
    assert first["metadata"]["tenant_id"] == "22222222-2222-4222-8222-222222222222"
    assert first["invoices"] != second["invoices"]


def test_validator_rejects_kept_promise_without_payment_by_grace_date() -> None:
    fixture = generate_synthetic_data()
    broken_promise = next(
        promise
        for promise in fixture["promises_to_pay"]
        if promise["status"] == "broken"
    )
    broken_promise["status"] = "kept"

    with pytest.raises(ValueError, match="timely payment evidence"):
        validate_synthetic_data(fixture)


def test_invoice_dates_cover_twelve_months_with_seasonal_distribution() -> None:
    fixture = generate_synthetic_data()
    invoices = fixture["invoices"]

    monthly_counts = {}
    for invoice in invoices:
        month = invoice["invoice_date"][:7]
        monthly_counts[month] = monthly_counts.get(month, 0) + 1

    # The generated history should cover 12 months.
    assert len(monthly_counts) == 13
    assert min(monthly_counts.values()) > 0

    # Seasonal weighting should create different monthly invoice counts.
    assert max(monthly_counts.values()) - min(monthly_counts.values()) >= 30


def test_import_sample_contains_messy_data_examples() -> None:
    import csv

    sample_path = ROOT_DIR / "data" / "demo" / "receivables_import_sample.csv"

    with sample_path.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 7

    invoice_numbers = [row["invoice_number"] for row in rows]
    assert len(invoice_numbers) > len(set(invoice_numbers))

    assert any(not row["phone"] for row in rows)
    assert any(not row["email"] for row in rows)

    dates = {row["invoice_date"] for row in rows}
    assert len(dates) > 1

    amounts = {row["amount"] for row in rows}
    assert any("EGP" in amount for amount in amounts)
    assert any("," in amount for amount in amounts)

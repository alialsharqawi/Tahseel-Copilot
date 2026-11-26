from __future__ import annotations

import argparse
import json
import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


DEFAULT_SEED = 2026
DEFAULT_REFERENCE_DATE = date(2026, 12, 15)
DEFAULT_TENANT_ID = uuid.UUID("11111111-1111-4111-8111-111111111111")
DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "demo" / "receivables.json"
)
NAMESPACE = uuid.UUID("7f4f6f62-bf08-4a5f-a1ed-a2b6e1ec9af5")
CENT = Decimal("0.01")


def _uuid(tenant_id: uuid.UUID, entity: str, index: int) -> uuid.UUID:
    return uuid.uuid5(NAMESPACE, f"{tenant_id}:{entity}:{index}")


def _money(value: Decimal) -> str:
    return str(value.quantize(CENT, rounding=ROUND_HALF_UP))


def _decimal(value: str) -> Decimal:
    return Decimal(value)


def _iso(value: date) -> str:
    return value.isoformat()


def _timestamp(value: date) -> str:
    return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc).isoformat()


def _seasonal_invoice_date(
    rng: random.Random, reference_date: date, index: int
) -> date:
    start = reference_date - timedelta(days=364)

    # Synthetic seasonal pattern for demo purposes only.
    monthly_weights = {
        1: 1.0,
        2: 1.0,
        3: 1.2,
        4: 1.2,
        5: 1.0,
        6: 0.9,
        7: 0.9,
        8: 0.9,
        9: 1.2,
        10: 1.2,
        11: 1.1,
        12: 1.1,
    }

    available_dates = [
        start + timedelta(days=day) for day in range((reference_date - start).days + 1)
    ]

    weights = [
        monthly_weights[available_date.month] for available_date in available_dates
    ]

    return rng.choices(available_dates, weights=weights, k=1)[0]


def generate_synthetic_data(
    *,
    seed: int = DEFAULT_SEED,
    reference_date: date = DEFAULT_REFERENCE_DATE,
    tenant_id: uuid.UUID = DEFAULT_TENANT_ID,
) -> dict[str, Any]:
    rng = random.Random(seed)
    archetypes = ["reliable"] * 72 + ["late"] * 30 + ["chronic_late"] * 18
    rng.shuffle(archetypes)
    collector_ids = [_uuid(tenant_id, "collector", index) for index in range(1, 4)]

    customers: list[dict[str, Any]] = []
    for index in range(120):
        archetype = archetypes[index]
        strategic = index % 5 == 0
        collector_index = (index % 3) + 1
        customers.append(
            {
                "id": str(_uuid(tenant_id, "customer", index)),
                "tenant_id": str(tenant_id),
                "name": f"Synthetic Distributor {index + 1:03d}",
                "phone": None if index % 17 == 0 else f"+20 100 000 {index:04d}",
                "email": None
                if index % 23 == 0
                else f"customer-{index + 1:03d}@example.synthetic",
                "credit_limit": _money(
                    Decimal(rng.choice((100000, 250000, 500000, 750000, 1000000)))
                ),
                "payment_terms": rng.choice(("Net 30", "Net 45", "Net 60")),
                "tier": "strategic" if strategic else "regular",
                "sales_rep": f"Synthetic Sales Rep {((index % 8) + 1):02d}",
                "assigned_collector": str(collector_ids[collector_index - 1]),
                "preferred_channel": rng.choice(("call", "whatsapp", "email")),
                "contact_person": f"Synthetic Contact {index + 1:03d}",
                "status": "active",
                "archetype": archetype,
            }
        )

    status_cycle: list[str] = ["paid"] * 975 + ["open"] * 375 + ["disputed"] * 150
    rng.shuffle(status_cycle)

    invoices: list[dict[str, Any]] = []
    for index in range(1500):
        customer_index = index % 120
        customer = customers[customer_index]
        archetype = customer["archetype"]
        invoice_date = _seasonal_invoice_date(rng, reference_date, index)
        terms = int(str(customer["payment_terms"]).split()[-1])
        due_date = invoice_date + timedelta(days=terms)
        amount = Decimal(rng.randint(15000, 750000)).quantize(
            CENT, rounding=ROUND_HALF_UP
        )
        if archetype == "chronic_late" and index % 4 == 0:
            amount = (amount * Decimal("1.35")).quantize(CENT, rounding=ROUND_HALF_UP)

        status = status_cycle[index]
        invoices.append(
            {
                "id": str(_uuid(tenant_id, "invoice", index)),
                "tenant_id": str(tenant_id),
                "customer_id": customer["id"],
                "invoice_number": f"SYN-{tenant_id.hex[:8].upper()}-{index + 1:04d}",
                "invoice_date": _iso(invoice_date),
                "due_date": _iso(due_date),
                "amount": _money(amount),
                "paid_amount": "0.00",
                "status": status,
                "dispute_reason": (
                    "Synthetic quantity disagreement" if status == "disputed" else None
                ),
                "disputed_by": (
                    customer["assigned_collector"] if status == "disputed" else None
                ),
                "disputed_at": (
                    _timestamp(min(reference_date, due_date + timedelta(days=10)))
                    if status == "disputed"
                    else None
                ),
                "archetype": archetype,
            }
        )

    payments: list[dict[str, Any]] = []
    payment_index = 0

    def add_payment(
        invoice: dict[str, Any],
        amount: Decimal,
        payment_date: date,
        method: str,
    ) -> None:
        nonlocal payment_index
        payments.append(
            {
                "id": str(_uuid(tenant_id, "payment", payment_index)),
                "tenant_id": str(tenant_id),
                "customer_id": invoice["customer_id"],
                "invoice_id": invoice["id"],
                "amount": _money(amount),
                "payment_date": _iso(payment_date),
                "method": method,
            }
        )
        payment_index += 1

    paid_invoices = [invoice for invoice in invoices if invoice["status"] == "paid"]
    open_invoices = [invoice for invoice in invoices if invoice["status"] == "open"]
    remaining_invoices = [
        invoice for invoice in invoices if invoice["status"] != "paid"
    ]

    extra_paid_invoices = rng.sample(paid_invoices, 925)
    extra_paid_ids = {invoice["id"] for invoice in extra_paid_invoices}
    for invoice in paid_invoices:
        amount = _decimal(invoice["amount"])
        invoice_date = date.fromisoformat(invoice["invoice_date"])
        due_date = date.fromisoformat(invoice["due_date"])
        archetype = invoice["archetype"]
        if invoice["id"] in extra_paid_ids:
            split = (amount * Decimal("0.40")).quantize(CENT, rounding=ROUND_HALF_UP)
            remainder = amount - split
            if archetype == "reliable":
                delay = rng.randint(-3, 5)
            elif archetype == "late":
                delay = rng.randint(8, 30)
            else:
                delay = rng.randint(25, 60)
            completion_date = max(
                invoice_date,
                min(reference_date, due_date + timedelta(days=delay)),
            )
            first_date = max(
                invoice_date,
                completion_date - timedelta(days=rng.randint(1, 30)),
            )
            add_payment(
                invoice,
                split,
                first_date,
                rng.choice(("bank_transfer", "cash", "check")),
            )
            add_payment(
                invoice,
                remainder,
                completion_date,
                rng.choice(("bank_transfer", "cash", "check")),
            )
            invoice["paid_amount"] = _money(amount)
            continue

        if archetype == "reliable":
            delay = rng.randint(-3, 5)
        elif archetype == "late":
            delay = rng.randint(8, 30)
        else:
            delay = rng.randint(25, 60)
        payment_date = min(reference_date, due_date + timedelta(days=delay))
        if payment_date < invoice_date:
            payment_date = invoice_date

        add_payment(
            invoice,
            amount,
            payment_date,
            rng.choice(("bank_transfer", "cash", "check")),
        )
        invoice["paid_amount"] = _money(amount)

    partial_count = 300
    partial_invoices = rng.sample(open_invoices, partial_count)
    for invoice in partial_invoices:
        amount = _decimal(invoice["amount"])
        invoice_date = date.fromisoformat(invoice["invoice_date"])
        ratio = Decimal(rng.choice(("0.20", "0.35", "0.50", "0.65")))
        paid = (amount * ratio).quantize(CENT, rounding=ROUND_HALF_UP)
        first = (paid * Decimal("0.45")).quantize(CENT, rounding=ROUND_HALF_UP)
        remainder = paid - first
        first_date = min(
            reference_date, invoice_date + timedelta(days=rng.randint(5, 35))
        )
        if first_date < invoice_date:
            first_date = invoice_date
        second_date = min(
            reference_date, first_date + timedelta(days=rng.randint(5, 25))
        )
        if second_date < first_date:
            second_date = first_date
        add_payment(
            invoice,
            first,
            first_date,
            rng.choice(("bank_transfer", "cash", "check")),
        )
        add_payment(
            invoice,
            remainder,
            second_date,
            rng.choice(("bank_transfer", "cash", "check")),
        )
        invoice["paid_amount"] = _money(paid)

    for invoice in remaining_invoices:
        invoice["paid_amount"] = "0.00"

    payment_totals = {invoice["id"]: Decimal("0.00") for invoice in invoices}
    for payment in payments:
        payment_totals[payment["invoice_id"]] += _decimal(payment["amount"])

    for invoice in invoices:
        invoice_paid = payment_totals[invoice["id"]]
        invoice["paid_amount"] = _money(invoice_paid)
        if invoice["status"] == "paid":
            if invoice_paid != _decimal(invoice["amount"]):
                raise ValueError(
                    f"Paid invoice {invoice['invoice_number']} has an inconsistent total"
                )
        elif invoice_paid >= _decimal(invoice["amount"]):
            raise ValueError(
                f"Non-paid invoice {invoice['invoice_number']} is fully paid"
            )
        elif invoice_paid > 0:
            invoice["status"] = (
                "disputed" if invoice["status"] == "disputed" else "open"
            )

    if len(payments) != 2500:
        raise ValueError(f"Expected 2,500 payment records, generated {len(payments)}")

    customer_by_id = {customer["id"]: customer for customer in customers}
    payment_history: dict[str, list[dict[str, Any]]] = {
        invoice["id"]: [] for invoice in invoices
    }
    for payment in payments:
        payment_history[payment["invoice_id"]].append(payment)
    for history in payment_history.values():
        history.sort(key=lambda payment: payment["payment_date"])

    grace_days = 2
    kept_invoices = rng.sample(paid_invoices, 15)
    broken_candidates = [
        invoice
        for invoice in open_invoices
        if date.fromisoformat(invoice["invoice_date"])
        <= reference_date - timedelta(days=grace_days)
    ]
    broken_invoices = rng.sample(broken_candidates, 11)
    pending_candidates = [
        invoice
        for invoice in open_invoices
        if invoice not in broken_invoices and invoice not in kept_invoices
    ]
    pending_invoices = rng.sample(pending_candidates, 4)
    promises: list[dict[str, Any]] = []

    for promise_index, invoice in enumerate(
        kept_invoices + broken_invoices + pending_invoices
    ):
        customer = customer_by_id[invoice["customer_id"]]
        invoice_amount = _decimal(invoice["amount"])
        invoice_date = date.fromisoformat(invoice["invoice_date"])
        if promise_index < 15:
            status = "kept"
            promised_amount = invoice_amount
            completion_date = max(
                date.fromisoformat(payment["payment_date"])
                for payment in payment_history[invoice["id"]]
            )
            promise_date = max(
                invoice_date,
                completion_date - timedelta(days=grace_days),
            )
            resolved_at = completion_date
        elif promise_index < 26:
            status = "broken"
            promised_amount = invoice_amount
            promise_date = max(
                invoice_date,
                min(
                    reference_date - timedelta(days=grace_days),
                    date.fromisoformat(invoice["due_date"]),
                ),
            )
            resolved_at = promise_date + timedelta(days=grace_days)
        else:
            status = "pending"
            promised_amount = (invoice_amount * Decimal("0.30")).quantize(
                CENT, rounding=ROUND_HALF_UP
            )
            promise_date = max(
                reference_date + timedelta(days=1),
                invoice_date,
            )
            resolved_at = None

        promises.append(
            {
                "id": str(_uuid(tenant_id, "promise", promise_index)),
                "tenant_id": str(tenant_id),
                "customer_id": invoice["customer_id"],
                "invoice_id": invoice["id"],
                "promised_amount": _money(promised_amount),
                "promise_date": _iso(promise_date),
                "status": status,
                "recorded_by": customer["assigned_collector"],
                "resolved_at": (
                    datetime.combine(
                        resolved_at,
                        datetime.min.time(),
                        tzinfo=timezone.utc,
                    ).isoformat()
                    if resolved_at
                    else None
                ),
            }
        )

    fixture = {
        "metadata": {
            "synthetic": True,
            "seed": seed,
            "reference_date": _iso(reference_date),
            "tenant_id": str(tenant_id),
            "required_user_ids": [str(user_id) for user_id in collector_ids],
            "promise_grace_days": grace_days,
            "description": "Synthetic receivables fixture for Tahseel AI",
        },
        "customers": customers,
        "invoices": invoices,
        "payments": payments,
        "promises_to_pay": promises,
    }
    validate_synthetic_data(fixture)
    return fixture


def validate_synthetic_data(fixture: dict[str, Any]) -> None:
    customers = fixture["customers"]
    invoices = fixture["invoices"]
    payments = fixture["payments"]
    promises = fixture["promises_to_pay"]
    metadata = fixture["metadata"]
    tenant_id = metadata["tenant_id"]
    reference_date = date.fromisoformat(metadata["reference_date"])
    grace_days = metadata["promise_grace_days"]
    required_user_ids = set(metadata["required_user_ids"])
    customer_by_id = {customer["id"]: customer for customer in customers}
    invoice_by_id = {invoice["id"]: invoice for invoice in invoices}

    if len(customer_by_id) != len(customers):
        raise ValueError("Customer IDs must be unique")
    if len(invoice_by_id) != len(invoices):
        raise ValueError("Invoice IDs must be unique")
    if len({invoice["invoice_number"] for invoice in invoices}) != len(invoices):
        raise ValueError("Invoice numbers must be unique")
    if len({payment["id"] for payment in payments}) != len(payments):
        raise ValueError("Payment IDs must be unique")
    if len({promise["id"] for promise in promises}) != len(promises):
        raise ValueError("Promise IDs must be unique")

    for customer in customers:
        if customer["tenant_id"] != tenant_id:
            raise ValueError("Customer has an inconsistent tenant")
        if customer["tier"] not in ("strategic", "regular"):
            raise ValueError("Customer tier is invalid")
        if customer["status"] not in ("active", "inactive"):
            raise ValueError("Customer status is invalid")
        if (
            customer["assigned_collector"] is not None
            and customer["assigned_collector"] not in required_user_ids
        ):
            raise ValueError("Customer references an unknown collector")

    payment_totals = {invoice_id: Decimal("0.00") for invoice_id in invoice_by_id}
    payment_history: dict[str, list[tuple[date, Decimal]]] = {
        invoice_id: [] for invoice_id in invoice_by_id
    }
    for payment in payments:
        if payment["tenant_id"] != tenant_id:
            raise ValueError("Payment has an inconsistent tenant")
        if payment["customer_id"] not in customer_by_id:
            raise ValueError("Payment references an unknown customer")
        if payment["invoice_id"] not in invoice_by_id:
            raise ValueError("Payment references an unknown invoice")
        invoice = invoice_by_id[payment["invoice_id"]]
        if payment["customer_id"] != invoice["customer_id"]:
            raise ValueError("Payment and invoice customers do not match")
        amount = _decimal(payment["amount"])
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        if date.fromisoformat(payment["payment_date"]) < date.fromisoformat(
            invoice["invoice_date"]
        ):
            raise ValueError("Payment predates its invoice")
        payment_totals[invoice["id"]] += amount
        payment_history[invoice["id"]].append(
            (date.fromisoformat(payment["payment_date"]), amount)
        )

    for history in payment_history.values():
        history.sort(key=lambda payment: payment[0])

    for invoice in invoices:
        if invoice["tenant_id"] != tenant_id:
            raise ValueError("Invoice has an inconsistent tenant")
        if invoice["customer_id"] not in customer_by_id:
            raise ValueError("Invoice references an unknown customer")
        invoice_date = date.fromisoformat(invoice["invoice_date"])
        if date.fromisoformat(invoice["due_date"]) < invoice_date:
            raise ValueError("Invoice due date cannot precede its invoice date")
        if invoice["status"] == "disputed":
            if (
                not invoice["dispute_reason"]
                or not invoice["disputed_by"]
                or invoice["disputed_by"] not in required_user_ids
                or not invoice["disputed_at"]
            ):
                raise ValueError("Disputed invoice metadata is incomplete")
            disputed_date = datetime.fromisoformat(invoice["disputed_at"]).date()
            if disputed_date < invoice_date or disputed_date > reference_date:
                raise ValueError("Disputed date is outside the invoice history")
        amount = _decimal(invoice["amount"])
        paid_amount = payment_totals[invoice["id"]]
        if paid_amount > amount:
            raise ValueError("Invoice paid amount exceeds its amount")
        if paid_amount != _decimal(invoice["paid_amount"]):
            raise ValueError("Invoice paid_amount cache is inconsistent")
        if invoice["status"] == "paid" and paid_amount != amount:
            raise ValueError("Paid invoice does not equal its amount")
        if invoice["status"] != "paid" and paid_amount >= amount:
            raise ValueError("Non-paid invoice is fully paid")
        if invoice["status"] not in ("open", "paid", "disputed"):
            raise ValueError("Invoice status is invalid")

    for promise in promises:
        if promise["tenant_id"] != tenant_id:
            raise ValueError("Promise has an inconsistent tenant")
        if promise["customer_id"] not in customer_by_id:
            raise ValueError("Promise references an unknown customer")
        if promise["invoice_id"] not in invoice_by_id:
            raise ValueError("Promise references an unknown invoice")
        invoice = invoice_by_id[promise["invoice_id"]]
        if promise["customer_id"] != invoice["customer_id"]:
            raise ValueError("Promise and invoice customers do not match")
        if promise["status"] not in ("pending", "kept", "broken"):
            raise ValueError("Promise status is invalid")
        if promise["recorded_by"] not in required_user_ids:
            raise ValueError("Promise references an unknown recorder")

        promise_date = date.fromisoformat(promise["promise_date"])
        invoice_date = date.fromisoformat(invoice["invoice_date"])
        promised_amount = _decimal(promise["promised_amount"])
        if promise_date < invoice_date:
            raise ValueError("Promise predates its invoice")
        if promised_amount <= 0 or promised_amount > _decimal(invoice["amount"]):
            raise ValueError("Promised amount is outside invoice bounds")

        payment_cutoff = promise_date + timedelta(days=grace_days)
        paid_by_cutoff = sum(
            (
                amount
                for payment_date, amount in payment_history[promise["invoice_id"]]
                if payment_date <= payment_cutoff
            ),
            Decimal("0.00"),
        )
        if promise["status"] == "pending":
            if promise_date <= reference_date or promise["resolved_at"] is not None:
                raise ValueError(
                    "Pending promise must have a future date and no resolution"
                )
        elif promise["status"] == "kept":
            if paid_by_cutoff < promised_amount or not promise["resolved_at"]:
                raise ValueError("Kept promise lacks timely payment evidence")
            resolved_date = datetime.fromisoformat(promise["resolved_at"]).date()
            if resolved_date < promise_date or resolved_date > payment_cutoff:
                raise ValueError("Kept promise resolution is outside its grace period")
        else:
            if payment_cutoff > reference_date or paid_by_cutoff >= promised_amount:
                raise ValueError(
                    "Broken promise is not past due with unpaid promise amount"
                )


def write_fixture(
    fixture: dict[str, Any],
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(fixture, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def _parse_reference_date(value: str) -> date:
    return date.fromisoformat(value)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a reproducible synthetic receivables fixture."
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--reference-date",
        type=_parse_reference_date,
        default=DEFAULT_REFERENCE_DATE,
    )
    parser.add_argument(
        "--tenant-id",
        type=uuid.UUID,
        default=DEFAULT_TENANT_ID,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    fixture = generate_synthetic_data(
        seed=args.seed,
        reference_date=args.reference_date,
        tenant_id=args.tenant_id,
    )
    output_path = write_fixture(fixture, args.output)
    print(
        f"Wrote {len(fixture['customers'])} customers, "
        f"{len(fixture['invoices'])} invoices, "
        f"{len(fixture['payments'])} payments, "
        f"and {len(fixture['promises_to_pay'])} promises to "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()

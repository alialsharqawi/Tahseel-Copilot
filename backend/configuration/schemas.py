from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_validator,
    model_validator,
)

RuleType = Literal["escalation", "grace_period", "limit", "review_required"]
Tone = Literal["formal", "friendly", "firm"]


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)


class RiskWeights(StrictSchema):
    days_overdue: int = Field(default=30, ge=0, le=100)
    historical_payment_delay: int = Field(default=25, ge=0, le=100)
    broken_promises: int = Field(default=25, ge=0, le=100)
    recent_payment_behavior: int = Field(default=20, ge=0, le=100)

    @model_validator(mode="after")
    def weights_total_one_hundred(self) -> RiskWeights:
        if sum(self.model_dump().values()) != 100:
            raise ValueError("Risk weights must total 100.")
        return self


class RiskCaps(StrictSchema):
    days_overdue: int = Field(default=60, gt=0)
    historical_payment_delay: int = Field(default=45, gt=0)
    broken_promises: int = Field(default=3, gt=0)
    recent_payment_behavior: int = Field(default=30, gt=0)


class UrgencySettings(StrictSchema):
    broken_promise_multiplier: float = Field(default=2.0, gt=0)
    broken_promise_window_days: int = Field(default=7, gt=0)
    escalation_crossing_multiplier: float = Field(default=2.0, gt=0)
    escalation_crossing_window_days: int = Field(default=7, gt=0)
    upcoming_promise_multiplier: float = Field(default=1.5, gt=0)
    upcoming_promise_window_days: int = Field(default=3, gt=0)
    no_contact_multiplier: float = Field(default=1.5, gt=0)
    follow_up_interval_days: int = Field(default=7, gt=0)
    default_multiplier: float = Field(default=1.0, gt=0)


class ReminderCap(StrictSchema):
    count: int = Field(gt=0)
    period_days: int = Field(gt=0)


class TenantSettingsSchema(StrictSchema):
    """Validated tenant settings with defaults explicitly stated in PRD §§11–12."""

    risk_weights: RiskWeights = Field(default_factory=RiskWeights)
    risk_caps: RiskCaps = Field(default_factory=RiskCaps)
    min_history_invoices: int = Field(default=3, gt=0)
    insufficient_history_ratio: float = Field(default=0.4, ge=0, le=1)
    urgency: UrgencySettings = Field(default_factory=UrgencySettings)
    escalation_trigger_days: tuple[int, ...] = (30, 60, 90)

    # These settings are described in the PRD, but §§11–12 do not specify defaults.
    promise_grace_days: int | None = Field(default=None, ge=0)
    grace_period_days: dict[str, int] | None = None
    reminder_cap: ReminderCap | None = None
    tone_defaults_by_tier: dict[Literal["strategic", "regular"], Tone] | None = None

    @field_validator("escalation_trigger_days")
    @classmethod
    def validate_escalation_triggers(cls, values: tuple[int, ...]) -> tuple[int, ...]:
        if not values or any(day <= 0 for day in values):
            raise ValueError("Escalation triggers must contain positive day values.")
        if tuple(sorted(set(values))) != values:
            raise ValueError("Escalation triggers must be strictly increasing.")
        return values

    @field_validator("grace_period_days")
    @classmethod
    def validate_grace_periods(
        cls, values: dict[str, int] | None
    ) -> dict[str, int] | None:
        if values is not None and any(days < 0 for days in values.values()):
            raise ValueError("Grace periods must not be negative.")
        return values


class PolicyRuleCreate(StrictSchema):
    name: str = Field(min_length=1)
    rule_type: RuleType
    condition: dict[str, JsonValue]
    outcome: dict[str, JsonValue]
    source_document_id: UUID
    source_section: str = Field(min_length=1)
    active: bool = True

    @field_validator("name", "source_section")
    @classmethod
    def strip_non_empty_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value must not be empty.")
        return normalized


class PolicyRuleUpdate(StrictSchema):
    name: str | None = Field(default=None, min_length=1)
    rule_type: RuleType | None = None
    condition: dict[str, JsonValue] | None = None
    outcome: dict[str, JsonValue] | None = None
    source_document_id: UUID | None = None
    source_section: str | None = Field(default=None, min_length=1)
    active: bool | None = None

    @field_validator("name", "source_section")
    @classmethod
    def strip_non_empty_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Value must not be empty.")
        return normalized

    @model_validator(mode="after")
    def source_reference_is_updated_together(self) -> PolicyRuleUpdate:
        source_fields = {"source_document_id", "source_section"}
        supplied_source_fields = source_fields.intersection(self.model_fields_set)
        if supplied_source_fields and supplied_source_fields != source_fields:
            raise ValueError(
                "source_document_id and source_section must be updated together."
            )
        return self


class PolicyRuleResponse(StrictSchema):
    id: UUID
    tenant_id: UUID
    name: str
    rule_type: RuleType
    condition: dict[str, JsonValue]
    outcome: dict[str, JsonValue]
    source_document_id: UUID
    source_section: str
    confirmed_by: UUID | None
    confirmed_at: datetime | None
    active: bool


class TenantSettingsResponse(StrictSchema):
    tenant_id: UUID
    settings: TenantSettingsSchema
    updated_by: UUID | None
    updated_at: datetime

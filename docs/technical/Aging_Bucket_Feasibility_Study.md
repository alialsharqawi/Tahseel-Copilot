# Aging-Bucket Customization Feasibility Study

**Status:** Feasibility analysis completed. Option A and the customization deferral were approved and recorded as D43/D44; T-013 implementation remains pending review of the documentation PR.

## Executive recommendation

For the MVP, use one fixed, documented set of buckets and keep it consistent across the platform. Defer organization-level presets until the team validates that different payment cycles need different reporting; defer fully custom buckets until there is evidence that presets are insufficient.

If custom reporting is later approved, settings should be **per tenant (employer/organization)**, not per user. Users in the same tenant must see the same aging for the same receivables and report date.

The original proposal's `61–90` and `90+` ranges overlap on day 90. D43 resolves this by keeping `61–90` and defining **Over 90** as `91+`.

## Repository evidence and current state

- T-013 is still queued; it is specified to implement outstanding, overdue, aging, and KPIs. D43 and the updated PRD now define the fixed boundaries and formulas; the engine is not implemented yet. See [BACKLOG.md](../team/BACKLOG.md) and [backlog.csv](../team/backlog.csv).
- T-010 has added a tenant-scoped `tenant_settings` table with a JSONB `settings` field. The PRD says settings are validated by a typed schema, but its list does not include aging buckets. There is no aging-specific setting, report table, or persisted report snapshot today. See [models.py](../../backend/db/models.py) and [Tahseel_AI_PRD.md](Tahseel_AI_PRD.md).
- The current backend exposes only `/health`; no receivables engine, KPI, Health Report, settings, or export endpoints exist yet. The PRD plans receivables and Health Report endpoints.
- The frontend is a bilingual starter page, not an implemented dashboard or settings screen. Static English and Arabic dashboard wireframes show `Current`, `1–30`, `31–60`, `61–90`, and `Over 90`. The glossary likewise describes aging by those example ranges. See [page.tsx](../../frontend/app/page.tsx), [English dashboard wireframe](../diagrams/wireframes/2_executive_dashboard_en.html), and [GLOSSARY.md](../../GLOSSARY.md).
- The PRD treats the Health Report as Should-tier and lists portfolio KPIs separately. DSO remains independent of aging buckets. No implemented Copilot prompts or export feature were found.

## 1. Configuration scope

**Recommend tenant-level configuration for any future customization.** A tenant is the employer/organization boundary already used by the data model. Per-platform settings are simplest and most comparable, but cannot address validated differences in payment cycles. Per-user settings would give coworkers different answers for the same portfolio and make reports, support, and audit trails hard to reconcile.

The UI should show one active organization-wide configuration. Changes should be permissioned and audited under the existing tenant-settings policy; do not infer that every Collector can change it.

## 2. Impact by surface

| Surface | Current repo state | If buckets become configurable |
|---|---|---|
| Aging calculation | Not implemented; assigned to T-013. | Accept validated bucket definitions as input; assign each unpaid balance exactly once using integer days past due as of a supplied report date. Keep `Current` separate and fixed. |
| Health Report | Planned as S3/T-032; wireframe has hard-coded labels. | Use the same definitions as the engine, return labels/ranges with amounts, and update the static EN/AR wireframes. |
| KPIs | T-013/PRD plans totals, overdue ratio, days beyond terms, and DSO. | These aggregate KPIs do not need bucket definitions. Do not derive DSO or escalation policy from reporting buckets. If bucket subtotals are exposed as KPIs, return their definitions alongside them. |
| Copilot tools/prompts | T-043/T-044 are planned; no prompt/tool implementation exists. The concept lists `get_portfolio_kpis`. | Supply bucket definitions and computed amounts from deterministic tools. Prompt the model to explain those results, not recalculate or invent ranges. Keep action/escalation rules separate. |
| Tests | T-013 has not started; existing backend tests do not test aging. | Add boundary, balance-reconciliation, configuration, and (if persisted) snapshot tests. See section 7. |
| DB/settings | `tenant_settings.settings` is tenant-scoped JSONB; no bucket keys or report table exist. | Add a typed settings field; no migration is required if the JSONB approach remains. Add report persistence only if historical reports must be reproducible. |
| API | Only `/health` is implemented. Receivables endpoints are PRD plans. | Include the active bucket definitions in Health Report/KPI responses. Add a tenant-settings read/update contract if users can select or edit configurations. |
| UI | Starter screen only; dashboard wireframe is static; no settings UI. | Render labels from API definitions in EN/AR. Presets need a selector; custom ranges need an editor and validation feedback. |
| Exports | No export endpoint or report-export requirement is specified; current product scope is CSV/Excel import. | If exports are later added, include the report date and exact bucket definitions used. Do not silently export custom totals without their ranges. |

## 3. Data model and report stability

The existing JSONB settings row is a natural home for tenant-level settings. For presets or custom definitions, use a typed structure conceptually like:

```json
{
  "aging": {
    "template": "standard_30_60_90",
    "overdue_upper_bounds": [30, 60, 90, null]
  }
}
```

Treat the array order as display order. `Current` is fixed and is not one of the configurable overdue buckets. A bound of `null` means the final bucket is open-ended. Derive localized labels from the ranges rather than storing arbitrary display strings; for example, bounds `[30, 60, 90, null]` render as `1–30`, `31–60`, `61–90`, `91+`. This avoids different labels for identical ranges and leaves translation to the UI.

If a generated report is persisted or can be revisited/exported later, store a snapshot of its `as_of_date` and bucket definitions (or an immutable settings version plus definitions). Otherwise a settings change could relabel old totals. There is no report entity today, so a snapshot is not needed for a transient response; return the definitions with every response instead.

## 4. Validation and enforcement

For presets/customization, a reasonable starting contract is **3–6 overdue buckets** (Current is additional), positive integer days, first range starts at day 1, contiguous non-overlapping ranges, strictly increasing finite upper bounds, and a final open-ended bucket. A finite upper bound should be capped; **3650 days** is a proposed guardrail, not an approved business rule.

- **API/domain validation is authoritative:** reject invalid edits with a clear validation error. Do not silently fall back to defaults for malformed saved settings.
- **UI validation** should give immediate feedback, but cannot be trusted as enforcement.
- **DB constraints** should preserve tenant ownership and non-null settings. With the existing JSONB design, enforce continuity/count in the typed application validator rather than a complex trigger. A normalized bucket table could add row-level constraints, but gaps across rows still need cross-row validation.
- `Current` should remain fixed as “not past due”; define the first overdue day explicitly. With calendar dates, a due date equal to the report date is Current and the next date is day 1 overdue.

D43 settles disputed aging: unpaid disputed balances are included in the applicable bucket totals and reported as a separate subtotal. They remain excluded from the ranked queue under the existing rules.

## 5. Copilot behavior and guardrails

Different tenant buckets do not require a separate prompt per tenant. The deterministic tool response should carry `as_of_date`, bucket ranges/labels, and amounts; the model should explain only those returned values. It must not infer that a bucket boundary is an escalation threshold, credit-policy rule, or recommended action. Existing structured policy rules and tenant escalation settings remain authoritative.

Add a prompt/evaluation case that asks about an account at a boundary and verifies the answer uses the tool's tenant-specific label and amount. Tool output and tests—not the LLM—remain the source of every financial number.

## 6. Comparability

Tenant-level buckets keep each employer internally consistent, but bucket totals are not directly comparable between employers. Platform-level analytics must either use a fixed canonical view or recompute from invoice-level days overdue; custom bucket totals cannot reliably be rebinned after aggregation.

There is no platform benchmarking feature in the current scope. Do not add a second “standard” dashboard for MVP. If cross-tenant benchmarking is approved later, define a canonical reporting view and calculate it from underlying invoice data, not from tenant bucket totals.

## 7. Testing impact

These are **incremental bucket-focused cases**, not a count of all T-013 tests:

- **Fixed defaults:** about 8–10 cases: Current/due-today, day 1, each boundary and the adjacent day, partial/paid balance treatment, no double-counting, and bucket totals reconcile to eligible outstanding.
- **Presets:** about 6–9 additional cases: default selection, every preset's boundaries, unknown preset rejection, tenant isolation, and consistent API/UI labels.
- **Fully custom:** about 10–15 additional cases: valid arbitrary ranges; gap, overlap, duplicate/decreasing bound, invalid count, non-integer/negative/over-limit bound, missing open-ended final bucket, tenant isolation, and saved-report snapshot surviving a settings change.

Essential in all options: test exact boundary and one-day-before/after assignments; prove each eligible outstanding amount appears once; and prove bucket totals sum to the eligible receivables total.

## 8. Options, effort, and T-013

Effort is a rough task-equivalent estimate; it assumes no unexpected UI/API infrastructure work.

| Option | Scope and trade-offs | Rough effort | T-013 difference |
|---|---|---:|---|
| **A. Fixed defaults only (approved for MVP)** | Lowest risk and strongest comparability; no employer flexibility. Use one explicit platform definition. | 1–2 task-equivalents: settle/document boundaries and implement/test the deterministic buckets; update static wireframe labels. | Implement a fixed default; add boundary and reconciliation tests. No settings dependency. |
| **B. Preset templates (later)** | Bounded flexibility for different payment cycles, with simpler validation than a free-form editor. Still limits employers to chosen templates. | 2–3 task-equivalents: typed tenant setting/template selection, API/report integration, and settings UI/localized labels. | Keep calculation deterministic but accept a validated template definition; test every template. Avoid making Core T-013 depend on Should T-016 until the settings contract is scheduled. |
| **C. Fully custom buckets (later, only if presets fail)** | Maximum flexibility; most validation, UI, support, historical-report, and comparability burden. | 4–6 task-equivalents: schema/validator, tenant settings API and permissions, custom editor, report snapshot/export contract, tool/prompt integration, and expanded tests. | Add a validated definitions input and tenant-setting resolution; test valid and invalid ranges, boundaries, isolation, and report snapshots. This materially expands T-013 and needs explicit dependency/scope review. |

## 9. Decision and upgrade trigger

The study's MVP recommendation was approved and recorded in the [Decision Log](../governance/Tahseel_AI_Decision_Log.md):

- **D43:** fixed due-date aging buckets (`Current`, `1–30`, `31–60`, `61–90`, `Over 90`/`91+`); disputed unpaid balances are included and flagged; DSO uses average opening/closing AR over credit sales, with null for zero sales and zero as the fallback when opening AR cannot be determined.
- **D44:** defer tenant customization. If a real customer or pilot demonstrates need, start with tenant-level presets editable only by Owner or Finance Manager.

The upgrade trigger is a demonstrated need from a real customer or pilot. Presets come before any fully custom ranges. Historical report snapshots and a Standard comparison view remain future design questions, not MVP requirements.

## Remaining future questions

1. If presets are introduced, must saved reports retain a settings snapshot, or should historical trends be recomputed under the active preset?
2. Is there a validated need for platform-level benchmarking that warrants a separate canonical Standard view?

# Tahseel AI — Adaptability Strategy

**Purpose:** How one platform can serve different B2B distributors, with different policies and behaviors, without changing the core code for each client.
**Status:** Design document, consolidated 31 October 2026. This file owns the multi-sector design (D35). Each pillar says what the MVP builds and what stays on the roadmap.
**Companions:** `Tahseel_AI_Decision_Log.md` (D21, D22, D23), `Tahseel_AI_Final_Concept.md`, `Tahseel_AI_PRD.md` (schema and API), `Tahseel_AI_Technical_Strength.md`.

---

## 1. Design Goal

Sector differences should be **configuration, not code**. An auto-parts distributor may grant 30 days and escalate quickly after a delay. A medical-supplies distributor may allow longer grace periods. The engine, the schema, and the agent stay the same; the tenant's settings and policy rules change.

The platform is not tied to a product category. It handles one commercial pattern: **credit sales that need tracking and human governance.**

**What we claim:** the design makes sector differences a matter of configuration. **What we do not claim:** that it has been validated across real sectors. The MVP demo will be run on one synthetic dataset, and optionally on two seeded tenant profiles, to show the same behavior in two configurations (see section 4).

---

## 2. Architecture for Adaptation

```text
+-------------------------------------------------------------+
| Data ingestion                                              |
| CSV / Excel adapter  [MVP]                                  |
| Odoo adapter, ETA adapter  [roadmap]                        |
+--------------------------------+----------------------------+
                                 | canonical schema (PRD, section 19)
                                 v
+-------------------------------------------------------------+
| Tenant configuration  [MVP]                                 |
| tenant_settings (weights, caps, grace periods, triggers,    |
| reminder cap, tone defaults) and policy_rules               |
+--------------------------------+----------------------------+
                                 |
                +----------------+----------------+
                v                                 v
+-------------------------------+  +-------------------------------+
| Deterministic engine          |  | Agent with policy RAG         |
| risk, priority, forecast,     |  | tools, citations, drafts      |
| rule evaluation               |  | (LLM never calculates)        |
+---------------+---------------+  +---------------+---------------+
                +----------------+----------------+
                                 v
+-------------------------------------------------------------+
| Human approval gateway, enforced at the API  [MVP]          |
| (tenant-isolated; configurable multi-step approval: roadmap)|
+-------------------------------------------------------------+
```

---

## 3. The Five Pillars

### Pillar 1: Data adapters and the canonical schema

**Challenge.** Companies keep data in different places: Excel sheets, ERP systems such as Odoo, or e-invoicing records.

**Design.** The engine never touches source structures. It runs on the canonical schema, which is the data model in the PRD (section 19). An **adapter** is a component that reads one source and returns canonical records plus a validation report.

| Canonical entity | Where it lives in the schema |
|---|---|
| Customer profile | `customers` (tier, sales rep, assigned collector, payment terms) |
| Invoice | `invoices` (invoice-level only; line items are not modeled in the MVP) |
| Payment terms | `customers.payment_terms` and each invoice's `due_date` |
| Historical transactions | `payments`, `promises_to_pay`, `customer_notes` |

| | Scope |
|---|---|
| **MVP** | The CSV/Excel adapter with column mapping (proposed by the LLM from headers and masked samples, confirmed by the user), validation, and preview. Cleaning covers date and number formats, trimmed text, and duplicate detection |
| **Stretch** | Phone-number normalization and handling of compound company names |
| **Roadmap** | Odoo and ETA e-invoicing adapters. An SAP adapter is not planned |

### Pillar 2: Configuration-driven engine

**Challenge.** Credit policies differ across sectors.

**Design.** No payment term, threshold, or weight is hard-coded.
- `tenant_settings` holds risk weights and caps, grace periods, escalation triggers, follow-up interval, reminder cap, and tone defaults. A typed schema validates it, and changes are written to the audit log.
- `policy_rules` holds structured rules (for example "manager review above 30 days overdue"), each linked to its source document and section and confirmed by a Finance Manager (D21).

| | Scope |
|---|---|
| **MVP** | Both tables, with defaults, evaluated by the deterministic engine. Rules are entered manually or loaded by the seed script |
| **Stretch** | Two seeded tenant profiles (for example a strict auto-parts profile and a longer-grace medical-supplies profile) so the demo can show the same data behaving differently |
| **Roadmap** | Extracting rules from policy documents with LLM help, followed by human confirmation. Installment payment plans are out of scope |

### Pillar 3: Tone and policy context

**Challenge.** Tone and communication style differ by sector and by relationship.

**Design.**
- Message tone options are **formal, friendly, and firm**. The default comes from the customer's tier (strategic or regular) and from the tenant's tone defaults (D23).
- The agent retrieves passages from the tenant's own policy documents (pgvector, with the tenant filter inside the query) and uses them to explain and cite. Drafts are **guided by** the retrieved policy and pass a rule-based check (no legal threats, no forbidden phrases). A human reviews every draft.

| | Scope |
|---|---|
| **MVP** | Tone options, tier-driven defaults, policy-guided drafts, the rule-based check |
| **Roadmap** | Per-tenant "brand voice" profiles learned from edits (needs real data) |

### Pillar 4: Tenant isolation and access control

**Challenge.** Several companies share the platform. No data may cross between them, and each company needs its own permission structure.

**Design.** `tenant_id` is on every table. All access goes through a tenant-scoped layer, and every vector query carries the tenant filter. Three roles are enforced on the server: Owner, Finance Manager, and Collector (a Collector sees only assigned customers). The permission matrix is in the Decision Log (D15, D30).

| | Scope |
|---|---|
| **MVP** | Three roles, a cross-tenant test |
| **Roadmap** | A Sales Manager role (to review or object to reminders for strategic clients before they go out) and a read-only Viewer role |

### Pillar 5: Approval pipeline

**Challenge.** Companies approve things differently. Some want the collector's approval for routine notices; others want finance and sales together for critical ones.

**Design (MVP).** A fixed routing, enforced at the API:
- A routine draft is approved by the Collector (for assigned customers), a Finance Manager, or the Owner.
- A recommendation flagged `requires_manager_review` by a policy rule goes to a Finance Manager or the Owner.
- A reminder beyond the configured cap needs a manager override.
- Every recommendation, approval, edit, rejection, and override is written to the append-only audit log.

**Roadmap.** A configurable multi-step pipeline, including a Sales sign-off step for strategic accounts. Until then, the relationship-aware recommendation `TALK_TO_SALES_REP` covers the need (D36).

---

## 4. What the MVP Shows

| Pillar | Built in the MVP | Roadmap | How the demo shows it |
|---|---|---|---|
| 1. Adapters | CSV/Excel adapter, mapping, validation, preview | Odoo, ETA | Upload a messy file and confirm the mapping |
| 2. Configuration | `tenant_settings`, `policy_rules`, defaults | LLM rule extraction | Change a weight or a rule and watch the score or outcome change with no code change; optionally switch between two seeded profiles |
| 3. Tone and context | Three tones, tier defaults, rule-based draft check | Learned brand voice | Switch tone on a draft |
| 4. Isolation and roles | Three roles, cross-tenant test | Sales Manager, Viewer | Switch role; show the cross-tenant test |
| 5. Approval | Fixed routing at the API | Configurable multi-step approval | Approve as a Collector, then see a flagged item go to a manager |
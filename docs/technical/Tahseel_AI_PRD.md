# Tahseel AI — Product Requirements Document (PRD)

**Product:** Tahseel AI  
**Category:** Agentic B2B Credit-Control Copilot  
**Primary Market:** Egypt  
**Primary Customer:** B2B distributors selling on credit  
**Status:** Detailed product specification, consolidated  
**Version:** 1.1  
**Date:** 2026-10-08 (original), 2026-10-31 (consolidated)

---

## How to read this document

This is the detailed specification: formulas, fields, API, and acceptance criteria. It describes the product for the in-scope items only. **Scope lives in `Tahseel_AI_Final_Concept.md` and decisions live in `Tahseel_AI_Decision_Log.md`; when this document disagrees with either, they win** (D35). Sections 11, 12, 13, 19 to 22, and 26 to 32 were rewritten in version 1.1 to match the decisions.

**Superseded statements from version 1.0**

| Topic | Version 1.0 said | Now |
|---|---|---|
| Agents (section 13) | Five agents | One orchestrator with grouped tools (D7) |
| Retrieval (section 14) | Hybrid retrieval and reranking | Vector search with metadata filters and citation; reranking is an optional upgrade (D9) |
| Orchestration (section 22) | LangGraph or equivalent | Plain tool-calling loop (D13) |
| Vector store (section 22) | pgvector, or Chroma | pgvector (D9) |
| Roles (sections 19 and 20) | Five roles | Three roles: Owner, Finance Manager, Collector (D15, D30) |
| Background jobs (section 22) | Celery and Redis | FastAPI background tasks |
| Demo dataset (sections 27 and 32) | 500 customers, 5,000 invoices | About 120 customers, 1,500 invoices; numbers come from the generator (D20) |
| Risk weights and priority (sections 11 and 12) | Example weights; exposure inside risk; collection probability inside priority | Default weights 30/25/25/20; exposure only in priority; collection probability only in the forecast (D34) |
| Actions (section 13) | Included `REVIEW_CREDIT_TERMS` | Removed; `TALK_TO_SALES_REP` added (D36) |
| Policy table (section 19) | `policies` | `policy_rules` and `document_chunks` (D21) |
| Memory | Not specified | Customer memory and conversation memory (D28), added to sections 19 and 21 |
| Plan and interviews (sections 31 and 37) | Written as if interviews and an 8-week plan would happen | A proposal only. No interviews have taken place. The real project plan is in the LMS documentation |
| Scope tiers | Not defined | Core, Should, Delivery (D29) |

---

## 1. Executive Summary

Tahseel AI is an **Agentic Credit-Control Copilot** for B2B distributors that sell on invoice credit and manage receivables through Excel, ERP exports, WhatsApp, phone calls, and manual follow-up.

The product does not act as a payment wallet, debt-collection agency, or autonomous credit decision-maker.

Instead, Tahseel AI helps a Finance Manager or Collector answer:

- Who should we follow up with today?
- Which overdue accounts are most important?
- Why is this customer considered high risk?
- What does the customer's payment history suggest?
- What does our credit policy allow?
- What should the collector do next?
- How much cash can we reasonably expect in 7 and 30 days?
- What message should we send?

Core loop:

```text
Receivables Data
      ↓
Analyze
      ↓
Risk + Priority
      ↓
Retrieve Relevant Credit Policy
      ↓
Recommend Next Action
      ↓
Human Approval
      ↓
Draft Message / Create Task
      ↓
Track Outcome
```

**Product promise:** Help B2B distributors collect receivables faster, prioritize their team's time, and improve cash visibility without removing human control.

---

## 2. Problem Statement

A typical distributor may have hundreds or thousands of invoices, different payment terms, partial payments, overdue invoices, promises to pay, customer-specific credit limits, multiple sales representatives, and finance collectors following customers manually.

The problem is not simply lack of data.

> **The company has data but cannot efficiently turn it into daily collection decisions.**

Current workflow:

```text
ERP / Excel
    ↓
Open spreadsheet
    ↓
Sort overdue invoices
    ↓
Check customer history
    ↓
Check payment terms
    ↓
Call / WhatsApp
    ↓
Record result manually
```

This creates:

- weak prioritization
- repetitive manual work
- delayed follow-up
- inconsistent collection decisions
- poor cash visibility
- difficulty measuring collector performance
- missed important accounts

---

## 3. Product Vision

> **Make receivables management proactive instead of reactive.**

Tahseel should evolve from a receivables dashboard into an **AI Credit-Control Operating Layer** that continuously turns receivables data and company policies into explainable recommendations.

---

## 4. Target Market

### Ideal Customer Profile

Egyptian B2B distributors with recurring invoice-based credit sales and an internal finance/collection team.

### Initial verticals

1. Auto parts
2. Sanitaryware / building materials
3. Food & beverage
4. Electrical supplies
5. Industrial supplies
6. Medical supplies

### Best initial customer characteristics

- 50+ active B2B customers
- recurring credit sales
- meaningful overdue receivables
- finance/collection employees
- Excel or ERP exports
- repeated customer follow-up
- documented payment terms
- willingness to provide anonymized historical data

---

## 5. Personas

### Finance Manager

**Goals:** improve cash collection, understand receivables, prioritize high-risk accounts, forecast cash, monitor collectors.

**Pain:** manual analysis and poor visibility.

### Collector (collection officer)

**Goals:** know who to contact, what to say, track promises, finish tasks quickly.

**Pain:** large customer lists and fragmented history.

### Sales Manager (an influencer; not a product role in the MVP)

**Goals:** understand payment behavior and coordinate with finance.

**Pain:** sales and finance operate separately.

### Owner / CFO

**Goals:** know expected cash and accounts threatening cash flow.

**Pain:** reports arrive late and lack explanation.

---

## 6. Jobs-to-be-Done

- When I start my day, I want to know which customers need attention first.
- When an invoice becomes overdue, I want its urgency and context.
- When I contact a customer, I want history and relevant policy immediately.
- When I follow up, I want an appropriate message draft.
- When management asks about future cash, I want a defensible 7/30-day forecast.
- When AI recommends an action, I want to know why.

---

## 7. Goals

### Primary

- Reduce manual receivables analysis.
- Prioritize collection work.
- Improve overdue-account visibility.
- Provide explainable risk scores.
- Provide policy-aware recommendations.
- Generate collection message drafts.
- Track promises to pay.
- Improve 7/30-day cash visibility.
- Maintain complete auditability.

### Non-goals

Tahseel AI will **not**:

- process payments
- hold customer money
- become a wallet
- automatically block customer credit
- automatically suspend customers
- automatically send WhatsApp messages in MVP
- make legally binding credit decisions
- replace finance managers
- act as a debt-collection agency
- provide legal advice
- guarantee payment
- recommend credit limits (storing a customer's credit limit as data is fine)

---

## 8. Scope

### MVP

The MVP is organized in three tiers (Core, Should, Delivery). The capability list is in `Tahseel_AI_Final_Concept.md`, section 3.

**Data**
- CSV/Excel import
- customers
- invoices
- payments
- payment terms
- collection notes, promises to pay, and call outcomes (recorded by the collector)
- customer tier, sales rep, and assigned collector

**Intelligence**
- days overdue
- outstanding balance
- payment behavior
- rule-based risk score
- collection priority
- policy RAG
- next-action recommendation
- message drafting
- 7/30-day cash forecast

**Interface**
- executive dashboard
- collection queue
- customer profile
- invoice details
- risk explanation
- policy/RAG panel
- tasks
- audit log

**AI**
- agent orchestration
- RAG
- tool calling
- human approval gate

### V1

- ERP integrations
- CRM integration
- WhatsApp Business integration
- advanced forecasting
- ML-based risk prediction
- automated task assignment
- collector analytics
- customer segmentation

### Future

- payment behavior prediction
- credit-limit recommendations
- approval-based workflow automation
- multi-branch support
- working-capital analytics
- industry benchmarks
- MENA expansion

---

## 9. Core User Stories

### Finance Manager

- See total outstanding receivables.
- See overdue receivables.
- See high-risk customers.
- See expected cash.
- Understand why a customer is high risk.
- Confirm policy rules and set tenant settings.

### Collector

- See a prioritized collection queue.
- See customer history before calling.
- See recommended next action.
- Generate a message draft.
- Record the result of a call as a note.
- Record a promise to pay.
- Mark an invoice as disputed.

### Owner

- Know whether collection is improving.
- Know which accounts threaten cash flow.
- Get an understandable summary.

---

## 10. Core Workflow

### 10.1 Data Import

```text
Upload Excel
     ↓
Column Mapping
     ↓
Validation
     ↓
Preview
     ↓
Import
```

Supported fields:

```text
customer_name
invoice_number
invoice_date
due_date
invoice_amount
paid_amount
payment_date
sales_rep
payment_terms
```

Import rules:

- Each row creates or updates the customer and the invoice. When `paid_amount` and `payment_date` are present, the importer also creates a payment row. An optional payments file (`invoice_number`, `payment_date`, `amount`) imports partial payments.
- `payments` is the source of truth for what has been paid. An invoice's `paid_amount` is a cached total that the engine recomputes from `payments`.
- `sales_rep` belongs to the customer. If rows of one customer carry different values, the preview shows a warning and the most recent value is kept.
- The column mapping may be proposed by the LLM from the column headers and a few masked sample rows. The user confirms the mapping before anything is imported.

### 10.2 Receivables Analysis

```text
Outstanding = Invoice Amount - Paid Amount
```

If today > due date:

```text
Days Overdue = Today - Due Date
```

Otherwise:

```text
Days Until Due = Due Date - Today
```

Overdue is computed from the due date and today. It is never stored.

```text
Overdue Exposure (customer) = sum of Outstanding of the customer's
                              overdue invoices that are not disputed
```

### 10.3 Customer-Level Analysis

Illustrative example. In the demo, the numbers come from the data generator (D20), which is configured to produce a customer like this one.

```text
Customer: ABC Trading

Outstanding:          EGP 420,000
Overdue:              EGP 310,000
Invoices:             17
Overdue invoices:     8
Oldest overdue:       52 days
Average delay:        32 days (last 12 months)
Recent average delay: 45 days (last 90 days)
Largest invoice:      EGP 120,000
Promises:             3
Broken promises:      2
```

---

## 11. Risk Scoring

### Principle

An explainable rule-based score. It estimates **how likely a customer is to pay late, from payment behavior only**. The amount owed is not part of it; the amount enters the priority (section 12). Do not pretend the MVP has sophisticated ML.

### Factors and default weights (D34)

| Factor | Default weight | Input | Points | Default cap |
|---|---:|---|---|---|
| Days overdue | 30 | Maximum days overdue among the customer's overdue, non-disputed invoices | `30 x min(days / cap, 1)` | 60 days |
| Historical payment delay | 25 | Average days paid after the due date over invoices paid in the last 12 months (invoices paid on time count as 0) | `25 x min(average / cap, 1)` | 45 days |
| Broken promises | 25 | Promises with status `broken` in the last 12 months | `25 x min(broken / cap, 1)` | 3 promises |
| Recent payment behavior | 20 | Decline = average delay of invoices paid in the last 90 days minus the 12-month average. No payment in the last 90 days while the customer has overdue invoices gives full points | `20 x min(max(decline, 0) / cap, 1)` | 30 days |

Rules:

- The weights, caps, and thresholds above are **defaults** stored in `tenant_settings` (D22). The weights must total 100.
- With fewer paid invoices than `min_history_invoices` (default 3), the historical-delay factor gives `insufficient_history_ratio` of its weight (default 0.4) and the explanation says "limited history".
- Each factor's points are rounded to an integer. The score is the sum of the rounded points, so the factors always add up to the score exactly.
- Risk levels apply to the integer score:

```text
0-30    LOW
31-60   MEDIUM
61-80   HIGH
81-100  CRITICAL
```

Every score must be explainable. Example for ABC Trading (illustrative):

```text
HIGH RISK: 70

+26: oldest overdue invoice is 52 days overdue
+18: historical average delay = 32 days
+17: 2 broken promises in the last 12 months
+09: payments slowing (recent average delay 45 days, was 32)
```

The overdue exposure (EGP 310K) is shown next to the score, not inside it.

Tests: the factor points add up to the score; each factor stays between 0 and its weight; the weights total 100; changing a weight in `tenant_settings` changes the score without a code change.

---

## 12. Collection Priority

Risk and priority are not identical. A low-risk customer with a very large overdue amount that crossed an escalation trigger yesterday can be more urgent than a small high-risk account.

```text
Priority = normalize( Risk x Overdue Exposure x Urgency )
```

- **Risk:** the risk score, 0 to 100 (section 11).
- **Overdue Exposure:** the sum of the customer's overdue, non-disputed outstanding amounts, in EGP (section 10.2).
- **Urgency:** a multiplier for time-sensitive events. The highest applicable value is used, and the reasons are shown. Defaults, stored in `tenant_settings`:

| Urgency | When |
|---|---|
| 2.0 | A promise to pay was broken in the last 7 days, or an overdue invoice crossed an escalation trigger (default 30, 60, or 90 days overdue) in the last 7 days |
| 1.5 | A promise to pay falls due in the next 3 days, or no contact has been recorded for longer than the follow-up interval (default 7 days) on an overdue account |
| 1.0 | Otherwise |

  A recorded contact is a note or call outcome, or an approved message draft.
- **Normalization:** `raw = Risk x Exposure x Urgency`; `Priority = round(100 x raw / highest raw in the current queue)`. The top account scores 100.
- **Not in the formula:** collection probability. It belongs to the forecast only (D34).
- **Who is in the queue:** customers with overdue, non-disputed exposure. Disputed invoices appear in a separate list (D23).
- The UI shows Risk, Overdue Exposure, Urgency, and the urgency reasons. If a few very large accounts dominate the ranking in tests, a logarithmic scale on exposure is the documented alternative; record any change in the Decision Log.

### Suggested action (rules only, no LLM)

The Collection Queue shows a suggested action computed by these default rules, evaluated in order (D36). Thresholds live in `policy_rules` and `tenant_settings`.

1. The customer's tier is `strategic`: `TALK_TO_SALES_REP`.
2. An escalation rule says the manager takes over (default: risk level CRITICAL, or 90 or more days overdue): `ESCALATE_TO_MANAGER`.
3. A promise to pay is pending and its date, plus the grace period, has not passed: `WAIT`.
4. The customer has a preferred channel in customer memory: that channel (`CALL`, `WHATSAPP`, or `EMAIL`).
5. Maximum days overdue is 7 or fewer and the risk level is LOW or MEDIUM: `WHATSAPP`.
6. Otherwise: `CALL`.

`requires_manager_review` is a separate flag set by a triggered policy rule (default: more than 30 days overdue). It does not change the action; it routes the approval to a Finance Manager or Owner.

---

## 13. Agentic Architecture

One orchestrator with grouped tools (D7), running a plain tool-calling loop (D13).

```text
User / Dashboard
       |
       v
Agent Orchestrator  (LLM + tool calling, every call logged and gated)
       |
       v
Tool groups:
  Receivables | Risk and Priority | Policy (rules + RAG) | Forecast
  History and Memory (read only) | Drafting | Tasks (after approval)
       |
       v
Recommendation (reasons + citations)
       |
       v
Human Review  (Approve / Edit / Reject)
       |
       v
Task / Draft / Audit log
```

**Orchestrator**
- understands the user request
- selects tools and combines their results
- explains risk and priority using tool output (it never calculates)
- never writes customer memory

Possible actions (D36):

```text
CALL
WHATSAPP            (a draft for a human to send)
EMAIL               (a draft for a human to send)
WAIT
ESCALATE_TO_MANAGER
TALK_TO_SALES_REP   (strategic accounts, before any contact)
```

The queue shows a rule-based **suggested action** (section 12). The agent shows a **recommendation** with reasons and citations. When they differ, the UI shows both and explains why.

Human approval remains mandatory for consequential actions.

---

## 14. RAG Design

### Knowledge sources

- credit policy
- collection policy
- payment terms
- customer contracts
- internal procedures
- escalation rules
- approved communication templates
- collector notes (customer memory, embedded)

### Example

User:

> What should we do with a customer 45 days overdue?

Layer 1: a structured rule is triggered by code.

```text
Rule: manager review above 30 days overdue
Source: Credit Policy, Section 4.2
```

Layer 2: the retrieved passage is used to explain and cite.

```text
Credit Policy, Section 4.2
(passage retrieved from the policy document)
```

Response:

> Based on the company's policy, this account should be escalated for Finance Manager review.

Citation:

```text
Credit Policy, Section 4.2
```

### Pipeline

```text
Documents
   ↓
Parse
   ↓
Chunk
   ↓
Metadata
   ↓
Embeddings
   ↓
Vector Store
   ↓
Vector Search + Metadata Filters
(tenant filter inside the query)
   ↓
Relevant Context
   ↓
LLM
   ↓
Answer + Citation
```

Metadata:

```text
tenant_id
document_id
document_type
policy_type
customer_id
effective_date
section
page
```

### RAG safety

If no relevant policy exists:

> I could not find a relevant company policy for this recommendation.

If policies conflict:

> Two policy documents appear to conflict. Human review is required.

The agent must never invent company policy.

Retrieved text, notes, and uploaded documents are untrusted input. They are data, not instructions (section 25).

---

## 15. Tools

### Receivables Query

Input:

```json
{"customer_id":"CUS-001"}
```

Returns:

```json
{
  "outstanding": 420000,
  "overdue": 310000,
  "overdue_days_max": 52
}
```

### Risk Calculator

Returns:

```json
{
  "score": 70,
  "level": "HIGH",
  "factors": [
    {"factor": "days_overdue", "points": 26, "detail": "oldest overdue invoice is 52 days overdue"},
    {"factor": "historical_delay", "points": 18, "detail": "average delay 32 days"},
    {"factor": "broken_promises", "points": 17, "detail": "2 broken promises in 12 months"},
    {"factor": "recent_behavior", "points": 9, "detail": "recent average delay 45 days, was 32"}
  ]
}
```

### Portfolio KPIs

Returns total outstanding, overdue amount and ratio, average days beyond terms, and DSO for a period (D32).

```text
Average Days Beyond Terms (period) =
  average, over invoices paid in the period, of
  max(0, payment_date - due_date)
```

Unpaid overdue invoices are not mixed into this average. They are reported separately: how many, and their average days overdue.

```text
DSO =
Average Accounts Receivable
/
Credit Sales
x
Number of Days
```

Days beyond terms is the primary metric. DSO is the secondary KPI and the unit that converts days into cash in the ROI model.

### Cash Forecast

Inputs:

- outstanding invoices
- due dates
- historical payment behavior
- promises to pay

Outputs:

```text
Expected Cash — 7 Days
Expected Cash — 30 Days
Confidence
```

The collection probability (the chance a payment arrives in the window, from the customer's history) is used here and only here (D34).

### Customer History

Returns:

- invoices
- payments
- overdue history
- promises
- broken promises
- collector notes
- customer tier, sales rep note, and dispute status

No tool writes customer memory (D28). Humans write it through the UI and the API.

### Policy Retrieval

Returns:

```text
document
section
content
citation
relevance
```

It also returns the policy rules triggered for the customer, each with its source document and section (D21).

### Message Draft Generator

Creates a draft using:

- customer
- invoice
- amount
- days overdue
- tone (formal, friendly, or firm)
- policy context
- customer tier (the tone default)

Every draft passes a rule-based check (no legal threats, no forbidden phrases) before it is shown (D23).

### Task Creator

Creates:

```text
Customer
Task
Priority
Due Date
Assigned Collector
Recommended Action
```

A task is created only from an approved recommendation.

---

## 16. Human-in-the-Loop

```text
AI Recommendation
       ↓
Human Review
       ↓
Approve / Edit / Reject
       ↓
Execute manually
```

The AI cannot:

- send messages automatically in MVP
- block credit
- change credit limits
- threaten legal action
- modify financial records
- write customer memory

Approval is enforced at the API. An execute endpoint rejects any recommendation whose status is not approved (AC-005); a UI bug cannot bypass it.

---

## 17. Dashboard

### Executive Dashboard

```text
Total Receivables
Overdue Receivables
High-Risk Exposure
Expected Cash — 7 Days
Expected Cash — 30 Days
Overdue Trend
Average Days Beyond Terms (trend)
DSO
Promise-to-Pay Fulfillment
```

### Collection Queue

| Customer | Outstanding | Overdue | Risk | Priority | Suggested action |
|---|---:|---:|---|---:|---|
| ABC | 420K | 310K | HIGH | 100 | CALL |
| XYZ | 210K | 60K | MEDIUM | 61 | WHATSAPP |

Disputed invoices are listed separately and do not take part in the ranking.

### Customer Profile

- customer information
- credit terms
- total purchases
- outstanding
- overdue
- payment history
- risk score
- risk explanation
- promises to pay
- collection history
- relevant policies and triggered rules
- customer tier, sales rep note, and dispute status
- notes and promises, with a form to record a note, a call result, and a promise to pay
- recommended action

### AI Recommendation Panel

```text
Recommended Action: CALL   (requires Finance Manager review)

Why?

• Oldest overdue invoice is 52 days overdue.
• Customer has EGP 310K overdue.
• Customer historically pays 32 days late.
• Two of three promises were broken.

Policy:

Credit Policy §4.2: accounts more than 30 days overdue
require Finance Manager review.
(rule triggered; passage retrieved to explain it)

Memory used:

Note by Ahmed, 12 Oct

[Approve]
[Edit]
[Reject]
```

---

## 18. Cash Forecast

### 7-Day

Estimate expected incoming cash from:

- invoices due soon
- overdue invoices likely to be collected
- promises to pay

### 30-Day

Expand across the next 30 days.

Always expose uncertainty:

```text
Expected: EGP 1.8M
Confidence: Medium
```

Forecast must never be presented as guaranteed cash.

Method (Should tier): each open invoice contributes `outstanding x probability of payment in the window`. The probability comes from that customer's history (for example, the share of the customer's past invoices paid within a number of days after the due date). Promises to pay are weighted by the customer's promise-keep rate. The output is a low, expected, and high range plus a confidence label. The label depends on how much history supports the estimate and how wide the range is; the rule is in code and tested.

A time-split backtest harness reruns the forecast as of past dates on the synthetic data and compares expected with actual cash. It is cut together with forecast sophistication (Decision Log, section E).

---

## 19. Data Model

This section is the single field-level definition. `Tahseel_AI_Final_Concept.md`, section 8, lists the tables. Every table except `tenants` carries `tenant_id`. "Overdue" is computed, never stored.

### tenants

```text
id
name
industry
created_at
```

### users

```text
id
tenant_id
name
email
password_hash
role
created_at
```

Roles (D15):

```text
OWNER
FINANCE_MANAGER
COLLECTOR
```

Sales Manager and Viewer are roadmap roles.

### customers

```text
id
tenant_id
name
phone
email
credit_limit           (stored as data; recommending limits is out of scope)
payment_terms
tier                   (strategic | regular)
sales_rep
assigned_collector     (user id; makes "assigned only" enforceable)
preferred_channel      (call | whatsapp | email; set by a human)
contact_person         (set by a human)
status                 (active | inactive)
created_at
```

### invoices

```text
id
tenant_id
customer_id
invoice_number
invoice_date
due_date
amount
paid_amount            (cache, recomputed from payments)
status                 (open | paid | disputed)
dispute_reason
disputed_by
disputed_at
created_at
```

A partially paid invoice is `open` with `paid_amount` greater than 0.

### payments

```text
id
tenant_id
customer_id
invoice_id
amount
payment_date
method
created_at
```

`payments` is the source of truth for what has been paid.

### promises_to_pay

```text
id
tenant_id
customer_id
invoice_id
promised_amount
promise_date
status                 (pending | kept | broken)
recorded_by
created_at
resolved_at
```

A human records a promise. The status is rule-derived: `kept` when payments reach the promised amount by the promise date plus the grace period (`promise_grace_days`, default 2), otherwise `broken` after that date.

### customer_notes

```text
id
tenant_id
customer_id
note_type              (collector | sales_rep | call_outcome)
text
embedding              (vector; D16)
author_id
source                 (ui | import)
created_at
deleted_at             (soft delete; see the audit log)
```

Customer memory. Written by humans only (D28). Every entry has author, timestamp, and source.

### recommendations

```text
id
tenant_id
customer_id
agent_run_id
action
reasons                (list of reasons)
citations              (triggered rules and retrieved passages)
requires_manager_review
status                 (pending | approved | edited | rejected)
decided_by
decided_at
decision_reason
created_at
```

### draft_versions

```text
id
tenant_id
recommendation_id
tone
original_text
edited_text
edit_reason
check_result           (output of the rule-based draft check)
created_by
created_at
```

### collection_tasks

```text
id
tenant_id
customer_id
recommendation_id
assigned_to
priority
action
due_at
status                 (pending | done | cancelled)
notes
created_by
created_at
```

### conversations

```text
id
tenant_id
user_id
customer_id            (optional)
created_at
```

### messages

```text
id
tenant_id
conversation_id
role                   (user | assistant | tool)
content
tool_calls
is_summary             (true for an LLM-written running summary, labeled AI-generated)
created_at
```

Conversation memory. Context only; never a source of facts (D28).

### documents

```text
id
tenant_id
name
type                   (credit_policy | collection_policy | payment_terms | template | contract | other)
storage_path
uploaded_by
effective_date
created_at
```

### document_chunks

```text
id
tenant_id
document_id
customer_id            (optional)
policy_type
section
page
effective_date
text
embedding              (vector)
created_at
```

### policy_rules

```text
id
tenant_id
name
rule_type              (escalation | grace_period | limit | review_required)
condition
outcome                (for example requires_manager_review, or a suggested action)
source_document_id
source_section
confirmed_by
confirmed_at
active
```

Replaces the version 1.0 `policies` table (D21). Entered manually or loaded by the seed script in the MVP.

### tenant_settings

```text
tenant_id
settings               (validated by a typed schema)
updated_by
updated_at
```

The settings hold: risk weights and caps, `min_history_invoices`, `insufficient_history_ratio`, urgency values and windows, escalation triggers, grace periods, `promise_grace_days`, follow-up interval, reminder cap (count and period), and tone defaults by tier (D22).

### risk_scores

```text
id
tenant_id
customer_id
score
level
factors                (factor, points, detail)
calculated_at
```

### agent_runs

```text
id
tenant_id
user_id
run_type
input
output
tools_used
status
model
prompt_tokens
completion_tokens
cost_estimate
latency_ms
created_at
```

### audit_logs

```text
id
tenant_id
user_id
action
entity_type
entity_id
before
after
created_at
```

Append-only. The application's database role has no update or delete permission on this table. Every recommendation (including ones that are never approved), approval, edit, rejection, tool call, memory edit or deletion, and task creation is written here.

---

## 20. Multi-Tenancy & RBAC

Every business object must include `tenant_id`.

A user from Company A must never access Company B data. All data access goes through a tenant-scoped layer, and every vector query carries the tenant filter inside the query itself. A cross-tenant test is required (AC-007).

### Roles

**Owner:** full access, including users and roles.

**Finance Manager:** receivables, risk, recommendations, policies and rules, settings, tasks, reports, and the executive dashboard.

**Collector:** assigned customers only, tasks, customer history, drafts, recording notes and promises, and marking invoices as disputed.

The complete permission matrix is in the Decision Log, D15 (extended by D30). Permissions are enforced on the server. Sales Manager and Viewer are roadmap roles.

---

## 21. API

Base:

```text
/api/v1
```

Every endpoint is tenant-scoped and role-checked on the server. An endpoint that executes something (creating a task, marking a draft as approved) rejects any recommendation that is not approved (AC-005).

### Auth

```http
POST /auth/login
```

### Customers

```http
GET /customers
GET /customers/{id}
PATCH /customers/{id}                  tier, sales_rep, assigned_collector, preferred channel
```

### Invoices

```http
GET /invoices
GET /invoices/{id}
POST /invoices/import/preview
POST /invoices/import
POST /invoices/{id}/dispute            set disputed (reason required)
DELETE /invoices/{id}/dispute          clear disputed (manager roles only)
```

### Receivables

```http
GET /receivables/summary
GET /receivables/overdue
GET /receivables/kpis                  days beyond terms, DSO, overdue ratio
GET /receivables/health-report
```

### Collection Queue and Risk

```http
GET /collection/queue
GET /customers/{id}/risk
POST /customers/{id}/risk/recalculate
```

### Customer memory (written by humans)

```http
GET /customers/{id}/notes
POST /customers/{id}/notes             note_type, text, optional promise (amount, date)
PATCH /customers/{id}/notes/{note_id}
DELETE /customers/{id}/notes/{note_id} soft delete, written to the audit log
GET /customers/{id}/promises
```

### Recommendations and drafts

```http
GET /collection/recommendations
POST /customers/{id}/drafts            generate a draft in a chosen tone
POST /collection/recommendations/{id}/approve   optional edited text and reason
POST /collection/recommendations/{id}/reject    reason
```

### Forecast

```http
GET /forecast?window=7|30
```

### Tasks

```http
GET /tasks
POST /tasks                            only from an approved recommendation
PATCH /tasks/{id}
```

### Documents, rules, and settings

```http
POST /documents
GET /documents
GET /policy-rules
POST /policy-rules
POST /policy-rules/{id}/confirm
GET /settings
PUT /settings
```

### Agent and conversations

```http
POST /agent/run                        optional conversation_id
GET /conversations/{id}/messages
```

### Audit

```http
GET /audit-logs
```

---

## 22. Tech Stack

### Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
PostgreSQL
```

### AI

```text
LLM access through OpenRouter, behind our own LLMClient interface (D12)
Plain tool-calling loop (D13)
Multilingual embedding model (D16)
RAG: vector search with metadata filters and citation
```

### Vector DB

pgvector in the same PostgreSQL (D9).

### Frontend

```text
Next.js / React
TypeScript
```

### Background Jobs

FastAPI background tasks.

### Deployment

```text
Docker
Docker Compose
HTTPS reverse proxy and public deployment (Delivery tier, D17)
```

---

## 23. System Architecture

```text
                  ┌───────────────┐
                  │ React / Next  │
                  │ Dashboard     │
                  └───────┬───────┘
                          │
                          ↓
                  ┌───────────────┐
                  │ FastAPI       │
                  │ API           │
                  └───────┬───────┘
                          │
          ┌───────────────┼────────────────┐
          ↓               ↓                ↓
   ┌────────────┐  ┌─────────────┐  ┌──────────────┐
   │ PostgreSQL │  │ AI Agent     │  │ File Storage │
   │ + pgvector │  │ Orchestrator │  │              │
   └────────────┘  └──────┬──────┘  └──────────────┘
                           │
             ┌─────────────┼─────────────┐
             ↓             ↓             ↓
        Risk Tools     RAG Tools     Forecast Tools
             │             │             │
             └─────────────┼─────────────┘
                           ↓
                         LLM
```

---

## 24. Security & Privacy

Minimum requirements:

- HTTPS
- password hashing
- secure authentication/session handling
- RBAC
- tenant isolation
- input validation
- file validation
- audit logs
- secrets outside source code
- encrypted backups
- least-privilege database access
- minimize PII in LLM prompts
- defined data-retention rules

For public demos, use synthetic data.

Do not place real customer financial data in a public repository.

Encryption: TLS in transit; encryption at rest is a deployment setting. LLM calls go through a third-party gateway, so the demo uses synthetic data only. Before real data is used, restrict the providers and review their retention settings (D12, D27).

---

## 25. AI Safety

### Hallucinated financial facts

If data does not contain a fact:

> I don't have enough data to determine this.

### Hallucinated policies

Only cite retrieved policy documents.

### Unauthorized decisions

AI cannot make final credit decisions.

### Unapproved communication

AI drafts; humans approve.

### Prompt injection

Retrieved passages, collector notes, and uploaded documents are untrusted input. They are data, not instructions. No tool runs because a document says so, and nothing executes without approval.

### Memory poisoning

The agent never writes customer memory. Only humans and rules do (D28).

---

## 26. Evaluation

Two tiers (D29). The **basic** eval is in the Core tier and is never cut: about 15 agent cases, about 10 RAG queries (including no-policy and conflicting-policy cases), about 5 safety tests, and the ablation. The larger plan in `Tahseel_AI_Technical_Strength.md` is a stretch. We report actual results, including weaknesses.

### Agent evaluation

Test:

- tool selection
- correct customer identification
- risk interpretation
- policy retrieval
- recommendation correctness
- absence of fabricated numbers

### RAG metrics

```text
Retrieval Recall
Citation Accuracy
Context Relevance
Answer Groundedness
```

### Recommendation metrics

```text
Top-priority precision
Human approval rate
Recommendation usefulness
Task completion rate
```

### Safety tests

- A prompt injection in a policy or a note does not trigger an action.
- Cross-tenant retrieval returns nothing.
- Nothing is sent or executed without approval.

### Ablation

The same questions answered by (a) an LLM given the raw CSV and (b) the tool-grounded system. Count wrong or fabricated numbers in each.

---

## 27. Demo Dataset

Create a synthetic distributor dataset with a generator (D20).

Example:

```text
about 120 customers
about 1,500 invoices
12 months history
about 2,500 payment records
about 30 promises to pay
about 20 policy documents
```

These are demo values, not market statistics. Numbers shown in documents and slides come from the generator; they are not typed by hand.

Include realistic patterns:

- reliable customers
- late payers
- chronic late payers
- high-value customers
- strategic and regular customers
- broken promises
- partial payments
- disputed invoices
- seasonal behavior
- messy data (missing fields, duplicates, format errors)
- policy documents with deliberately conflicting sections, and questions with no matching policy (for the RAG eval)

---

## 28. KPIs

### Business

```text
Average Days Beyond Terms   (primary, D32)
DSO                         (secondary; converts days to cash)
Overdue Receivables
Collection Rate
Cash Collected
Expected vs Actual Cash
```

Formulas for days beyond terms and DSO are in section 15 (Portfolio KPIs).

### Operational

```text
Collector Time per Account
Tasks Completed
Follow-up Completion Rate
Promise-to-Pay Fulfillment
```

### Product

```text
Daily Active Finance Users
Recommendation Approval Rate
AI Recommendation Acceptance
Time Saved
```

These are measures to collect in a pilot. On synthetic data they prove the pipeline, not impact.

---

## 29. Success Criteria

The demo checklist is kept in one place: `Tahseel_AI_Final_Concept.md`, section 11. Section 30 below holds the acceptance criteria that make each item testable.

---

## 30. Acceptance Criteria

AC-001 to AC-010 and AC-014 are Core. AC-008, AC-011, AC-012, and AC-013 are Should.

### AC-001 Data Import

Given a valid CSV/XLSX file, the system maps fields, validates records, and shows a preview before import.

### AC-002 Overdue Detection

Given an invoice with a due date before today, overdue days are calculated correctly.

### AC-003 Risk Explanation

Every risk score has human-readable factors.

### AC-004 RAG

Every policy-based recommendation contains a source citation.

### AC-005 Human Approval

No external communication can be executed without explicit human approval.

### AC-006 Auditability

Every AI recommendation, approval, edit, and rejection is logged, including recommendations that are never approved. The audit log is append-only.

### AC-007 Tenant Isolation

A tenant cannot access another tenant's records.

### AC-008 Forecast

Forecasts distinguish expected cash from guaranteed cash.

### AC-009 Customer Memory

A Collector can record a note, a call result, and a promise to pay. They appear in the customer's history, carry author, timestamp, and source, and the agent can cite them. The agent has no way to write them.

### AC-010 Risk Arithmetic

The factor points add up to the score, the weights total 100, and each factor stays within its weight. Changing a weight in `tenant_settings` changes the score without a code change.

### AC-011 Policy Rules

A triggered rule is shown with its source document and section. Changing a rule or a setting changes the outcome without a code change. The system never blocks shipping or credit.

### AC-012 Disputes

A disputed invoice leaves the ranked queue, appears in the Disputed list, pauses follow-up, and alerts the manager. A Collector can set the status on assigned customers; only a manager role can clear it.

### AC-013 Reminder Cap

Beyond the configured cap, a draft needs a manager override.

### AC-014 Role Enforcement

A Collector cannot see unassigned customers and cannot approve a recommendation flagged for manager review. This is enforced at the API.

---

## 31. 8-Week Capstone Plan

This was the original proposal. It has not been executed as written. The real project plan, with dates and owners, is in the LMS documentation (Project Planning).

### Week 1 — Discovery + Data

- define ICP
- talk to potential distributors if access exists (optional)
- map current workflow
- create synthetic dataset
- finalize schema

**Deliverable:** problem statement + data model (validation is a later step)

### Week 2 — Backend Foundation

- FastAPI
- PostgreSQL
- authentication
- tenant model
- customers
- invoices
- payments

**Deliverable:** working backend

### Week 3 — Receivables Intelligence

- outstanding calculation
- overdue calculation
- customer aggregation
- risk rules
- priority score

**Deliverable:** receivables engine

### Week 4 — RAG

- document ingestion
- chunking
- embeddings
- retrieval
- citations
- policy testing

**Deliverable:** policy RAG

### Week 5 — Agent

- agent orchestrator
- tool calling
- risk tool
- receivables tool
- policy tool
- forecast tool
- recommendation generation

**Deliverable:** working agent

### Week 6 — Dashboard

- executive dashboard
- collection queue
- customer profile
- AI recommendation panel
- tasks
- audit logs

**Deliverable:** usable product

### Week 7 — Integration + Evaluation

- connect frontend/backend
- agent evaluations
- RAG evaluations
- security testing
- error handling
- logging

**Deliverable:** production-like MVP

### Week 8 — Deployment + Demo

- Docker
- deployment
- HTTPS
- monitoring
- seed data
- demo script
- documentation

**Deliverable:** deployed Tahseel AI (Delivery tier; a recorded demo is the fallback, D17)

---

## 32. Demo Scenario

A distributor has (D20):

```text
about 120 customers
about 1,500 invoices
```

Dashboard (values come from the generator):

```text
Receivables:        EGP [X]
Overdue:            EGP [Y]
High Risk:          EGP [Z]
Expected 7 Days:    EGP [A]
Expected 30 Days:   EGP [B]
```

System identifies (illustrative; the generator is configured to produce a customer like this):

```text
ABC Trading
```

Risk:

```text
70 — HIGH
```

Explanation:

```text
Oldest overdue invoice: 52 days
EGP 310K overdue
Historical average delay: 32 days
2 broken promises
```

Agent reads memory, retrieves:

```text
Credit Policy §4.2   (rule triggered, passage retrieved)
```

Recommendation:

```text
CALL, requires Finance Manager review
```

Then:

```text
Generate Draft
```

Tahseel creates a professional Arabic follow-up draft.

Finance Manager edits and approves.

System creates:

```text
Collection Task
Assigned: Ahmed
Priority: HIGH
Due: Today
```

Everything is logged.

The Collector then records the call result: a note and a promise to pay. A follow-up question in the same chat is answered with conversation memory.

A second customer, a strategic account, shows the recommendation `TALK_TO_SALES_REP`.

---

## 33. Why This Is Agentic

A normal chatbot:

```text
User → Question → LLM → Answer
```

Tahseel:

```text
User
 ↓
Understand Goal
 ↓
Select Tools
 ↓
Query Financial Data
 ↓
Calculate Risk
 ↓
Retrieve Policy
 ↓
Evaluate Context
 ↓
Recommend Action
 ↓
Generate Draft
 ↓
Human Approval
 ↓
Create Task
 ↓
Audit
```

The agent is valuable because it coordinates **tools + business context + policy + human approval**.

---

## 34. Why This Is Real RAG

RAG is not used just to answer generic questions.

It grounds recommendations in company-specific knowledge:

```text
Customer Situation
+
Company Policy
+
Payment History
+
Receivables Data
=
Policy-Aware Recommendation
```

---

## 35. Why This Is Production-Minded

The project includes:

- authentication
- RBAC
- multi-tenancy
- audit logs
- data validation
- human approval
- observability
- AI evaluation
- RAG evaluation
- error handling
- Docker
- deployment
- database
- API
- frontend
- synthetic data
- security controls

Deployment and observability beyond basic logging belong to the Delivery tier and are scheduled after the core slice (D17, D29).

It therefore demonstrates a complete AI product rather than an isolated model.

---

## 36. Risks & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| No real distributor access | High | Use synthetic data, label every claim by evidence level, and run interviews after the capstone (the validation plan is in the business file) |
| No real data | High | Synthetic + anonymized pilot data |
| Bad Excel formats | Medium | Mapping + validation |
| LLM hallucination | High | Tool-grounded answers + RAG citations |
| Wrong recommendation | High | Human approval |
| Policy conflicts | High | Surface conflict + human review |
| Poor forecast | Medium | Show confidence and assumptions |
| Scope creep | High | Strict MVP |
| WhatsApp integration complexity | Medium | Draft-only MVP |
| Security mistakes | High | RBAC + tenant isolation + audit |

---

## 37. Open Validation Questions

Open validation questions for interviews. No interview has taken place yet, so none of these is answered. The same list, with assumptions and kill criteria, is in `Tahseel_AI_Business_Strength.md`.

### Operations

1. How many customers buy on credit?
2. How many invoices are open at any time?
3. How are overdue invoices currently tracked?
4. Who follows up?
5. How are priorities decided?

### Pain

6. What is hardest about collection?
7. How much time is spent on follow-up?
8. Which customers become problematic?
9. What happens when a promise is broken?

### Data

10. Can you export invoices to Excel?
11. Do you have payment history?
12. Do you record collection notes?
13. Do you have documented credit policies?

### Buying

14. Who would buy this?
15. What would make you pay?
16. What would prevent adoption?
17. Would you allow a pilot using anonymized data?

---

## 38. Monetization Hypothesis

Initial model:

```text
Monthly SaaS Subscription
+
Setup / Data Migration Fee
```

Possible pricing dimensions:

- number of customers
- number of invoices
- number of finance users
- AI usage
- integrations

Do not finalize pricing before customer interviews.

---

## 39. Product Expansion

Start:

```text
Receivables Prioritization
        ↓
Risk Intelligence
        ↓
Cash Forecasting
        ↓
Collection Workflow
        ↓
Credit Intelligence
        ↓
Finance Operations Copilot
        ↓
B2B Working-Capital Intelligence Platform
```

---

## 40. Final MVP Definition

The MVP is complete when a real or synthetic distributor can:

```text
1. Upload receivables data
        ↓
2. See outstanding + overdue invoices
        ↓
3. See customer risk
        ↓
4. See prioritized collection queue
        ↓
5. Ask the AI about a customer
        ↓
6. AI uses financial tools
        ↓
7. AI retrieves company policy
        ↓
8. AI explains recommendation
        ↓
9. AI drafts a follow-up message
        ↓
10. Human approves/edits
        ↓
11. Task is created
        ↓
12. Action is audited
        ↓
13. Collector records the call result (note + promise)
        ↓
14. Manager sees cash forecast (Should tier)
```

---

## 41. Definition of Done

Core items must be checked. Should and Delivery items follow the tiers in `Tahseel_AI_Final_Concept.md`.

- [ ] Backend deployed.
- [ ] Frontend deployed.
- [ ] PostgreSQL database working.
- [ ] Authentication implemented.
- [ ] RBAC implemented.
- [ ] Tenant isolation tested.
- [ ] Three roles enforced on the server.
- [ ] Customer memory can be written (notes, call results, promises) and is used by the agent.
- [ ] Policy rules are evaluated by code and cited with their source.
- [ ] Excel/CSV import works.
- [ ] Receivables calculations tested.
- [ ] Risk scoring works.
- [ ] Collection prioritization works.
- [ ] RAG works with citations.
- [ ] Agent uses at least 3 meaningful tools.
- [ ] Human approval gate works.
- [ ] Message drafting works.
- [ ] Cash forecast works.
- [ ] Audit log works.
- [ ] Agent evaluation set created.
- [ ] RAG evaluation set created.
- [ ] Synthetic demo dataset created.
- [ ] Docker deployment works.
- [ ] Error handling implemented.
- [ ] Demo scenario rehearsed.
- [ ] README/documentation completed.

---

## 42. One-Sentence Product Definition

> **Tahseel AI is an agentic credit-control copilot that helps Egyptian B2B distributors prioritize overdue receivables, understand customer risk, apply company credit policies, forecast expected cash, and prepare collection actions — with humans always in control.**

---

## 43. Product Principle

> **Do not automate the decision before you automate the information needed to make the decision.**

Tahseel's first job is not:

> "Collect the money automatically."

Its first job is:

> **Make the finance team know exactly where to focus, why, and what to do next.**

That is the foundation on which later automation can safely be built.
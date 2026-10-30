# Tahseel AI — Product Requirements Document (PRD)

**Product:** Tahseel AI  
**Category:** Agentic B2B Credit-Control Copilot  
**Primary Market:** Egypt  
**Primary Customer:** B2B distributors selling on credit  
**Status:** Capstone-ready Product Definition  
**Version:** 1.0  
**Date:** 2026-10-08

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

### Collection Officer

**Goals:** know who to contact, what to say, track promises, finish tasks quickly.

**Pain:** large customer lists and fragmented history.

### Sales Manager

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

---

## 8. Scope

### MVP

**Data**
- CSV/Excel import
- customers
- invoices
- payments
- payment terms
- collection notes

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

### Collector

- See a prioritized collection queue.
- See customer history before calling.
- See recommended next action.
- Generate a message draft.
- Record the result.
- Record a promise to pay.

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

### 10.3 Customer-Level Analysis

Example:

```text
Customer: ABC Trading

Outstanding:       EGP 420,000
Overdue:           EGP 310,000
Invoices:          17
Overdue invoices:  8
Average delay:     21 days
Largest invoice:   EGP 120,000
Promises:          3
Broken promises:   1
```

---

## 11. Risk Scoring

### MVP principle

Start with an explainable rule-based score. Do not pretend the MVP has sophisticated ML.

Example:

```text
Risk Score =
Overdue Severity
+ Payment Delay History
+ Broken Promise History
+ Outstanding Exposure
+ Recent Payment Behavior
```

Example weights:

| Factor | Weight |
|---|---:|
| Days overdue | 25% |
| Historical payment delay | 20% |
| Broken promises | 20% |
| Outstanding amount | 20% |
| Recent payment behavior | 15% |

Risk levels:

```text
0–30    LOW
31–60   MEDIUM
61–80   HIGH
81–100  CRITICAL
```

Every score must be explainable.

Example:

```text
HIGH RISK

+22: 43 days overdue
+18: historical average delay = 27 days
+15: 1 broken promise
+12: high outstanding exposure
+08: payment frequency declining
```

---

## 12. Collection Priority

Risk and priority are not identical.

A small high-risk customer may be less urgent than a large customer with a major invoice due tomorrow.

Conceptually:

```text
Priority =
Risk
× Exposure
× Urgency
× Collection Probability
```

The final implementation should normalize the result and expose its major factors.

---

## 13. Agentic Architecture

```text
                    ┌──────────────────┐
                    │ User / Dashboard │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ Agent Orchestrator│
                    └────────┬─────────┘
                             │
        ┌────────────────────┼─────────────────────┐
        ↓                    ↓                     ↓
┌───────────────┐   ┌────────────────┐   ┌─────────────────┐
│ Risk Analysis │   │ Policy RAG     │   │ Cash Forecast   │
│ Agent         │   │ Retrieval      │   │ Tool            │
└───────┬───────┘   └───────┬────────┘   └────────┬────────┘
        │                   │                     │
        └───────────────────┼─────────────────────┘
                            ↓
                 ┌─────────────────────┐
                 │ Recommendation Agent│
                 └──────────┬──────────┘
                            ↓
                    ┌──────────────┐
                    │ Human Review │
                    └──────┬───────┘
                           ↓
                ┌─────────────────────┐
                │ Task / Draft / Log  │
                └─────────────────────┘
```

### Agents

**Orchestrator**
- understands user request
- selects tools
- combines results

**Risk Analysis Agent**
- analyzes customer history
- calls risk calculator
- explains risk

**Collection Prioritization Agent**
- ranks customers
- explains priority

**Policy Agent**
- retrieves relevant policies
- provides citations

**Recommendation Agent**
- combines customer data, risk, policy, history
- recommends next action

Possible actions:

```text
CALL
WHATSAPP
EMAIL
WAIT
ESCALATE_TO_MANAGER
REVIEW_CREDIT_TERMS
```

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

### Example

User:

> What should we do with a customer 45 days overdue?

Retrieved:

```text
Credit Policy — Section 4.2
Customers > 30 days overdue require Finance Manager review.
```

Response:

> Based on the company's policy, this account should be escalated for Finance Manager review.

Citation:

```text
Credit Policy — Section 4.2
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
Hybrid Retrieval
   ↓
Reranking
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
  "overdue_days_max": 43
}
```

### Risk Calculator

Returns:

```json
{
  "score": 78,
  "level": "HIGH",
  "factors": []
}
```

### DSO Calculator

Conceptually:

```text
DSO =
Average Accounts Receivable
/
Credit Sales
×
Number of Days
```

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

### Customer History

Returns:

- invoices
- payments
- overdue history
- promises
- broken promises
- collector notes

### Policy Retrieval

Returns:

```text
document
section
content
citation
relevance
```

### Message Draft Generator

Creates a draft using:

- customer
- invoice
- amount
- days overdue
- tone
- policy context

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
Collection Performance
```

### Collection Queue

| Customer | Outstanding | Overdue | Risk | Priority | Action |
|---|---:|---:|---|---:|---|
| ABC | 420K | 310K | HIGH | 95 | CALL |
| XYZ | 210K | 60K | MEDIUM | 61 | WHATSAPP |

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
- relevant policies
- recommended action

### AI Recommendation Panel

```text
Recommended Action: CALL

Why?

• Invoice is 43 days overdue.
• Customer has EGP 310K overdue.
• Customer historically pays 21 days late.
• One recent promise was broken.

Policy:

Credit Policy §4.2 recommends manager review
for accounts >30 days overdue.

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

---

## 19. Data Model

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
role
created_at
```

Roles:

```text
OWNER
FINANCE_MANAGER
COLLECTOR
SALES_MANAGER
VIEWER
```

### customers

```text
id
tenant_id
name
phone
email
credit_limit
payment_terms
status
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
paid_amount
status
sales_rep
created_at
```

### payments

```text
id
tenant_id
customer_id
invoice_id
amount
payment_date
method
```

### promises_to_pay

```text
id
tenant_id
customer_id
invoice_id
promised_amount
promise_date
status
created_at
```

### collection_tasks

```text
id
tenant_id
customer_id
assigned_to
priority
action
due_at
status
notes
```

### policies

```text
id
tenant_id
title
document_id
section
effective_date
```

### documents

```text
id
tenant_id
name
type
storage_path
uploaded_by
created_at
```

### risk_scores

```text
id
tenant_id
customer_id
score
level
factors
calculated_at
```

### agent_runs

```text
id
tenant_id
user_id
agent_type
input
output
tools_used
status
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

---

## 20. Multi-Tenancy & RBAC

Every business object must include `tenant_id`.

A user from Company A must never access Company B data.

### Roles

**Owner:** full access.

**Finance Manager:** receivables, risk, recommendations, policies, tasks, reports.

**Collector:** assigned customers, tasks, customer history, drafts.

**Sales Manager:** customer payment behavior and relevant reports.

**Viewer:** read-only.

---

## 21. API

Base:

```text
/api/v1
```

### Auth

```http
POST /auth/login
```

### Customers

```http
GET /customers
GET /customers/{id}
```

### Invoices

```http
GET /invoices
GET /invoices/{id}
POST /invoices/import
```

### Receivables

```http
GET /receivables/summary
GET /receivables/overdue
```

### Risk

```http
GET /customers/{id}/risk
POST /customers/{id}/risk/recalculate
```

### Recommendations

```http
GET /collection/recommendations
POST /collection/recommendations/{id}/approve
POST /collection/recommendations/{id}/reject
```

### Tasks

```http
GET /tasks
POST /tasks
PATCH /tasks/{id}
```

### Documents

```http
POST /documents
GET /documents
```

### Agent

```http
POST /agent/run
```

---

## 22. Suggested Tech Stack

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
LLM API
LangGraph or equivalent orchestration
Embeddings
RAG
Reranking
```

### Vector DB

Prefer PostgreSQL + pgvector for MVP to reduce infrastructure.

Alternative:

```text
Chroma
```

### Frontend

```text
Next.js / React
TypeScript
```

### Background Jobs

```text
Celery + Redis
```

or a simpler background-worker architecture.

### Deployment

```text
Docker
Docker Compose
Cloud VM / managed services
HTTPS
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

---

## 26. Evaluation

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

---

## 27. Demo Dataset

Create a synthetic distributor dataset.

Example:

```text
500 customers
5,000 invoices
12 months history
10,000 payment records
100+ promises to pay
20 policy documents
```

These are demo values, not market statistics.

Include realistic patterns:

- reliable customers
- late payers
- chronic late payers
- high-value customers
- broken promises
- partial payments
- seasonal behavior

---

## 28. KPIs

### Business

```text
Overdue Receivables
DSO
Collection Rate
Cash Collected
Expected vs Actual Cash
```

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

---

## 29. Success Criteria

The MVP must demonstrate that:

1. A finance manager can upload receivables data.
2. The system validates and imports it.
3. The dashboard calculates receivables.
4. Overdue invoices are identified.
5. Risk is explainable.
6. Customers are prioritized.
7. The agent answers receivables questions using tools.
8. RAG retrieves company policy.
9. Recommendations are policy-grounded.
10. A follow-up message can be drafted.
11. Human approval is required.
12. A collection task can be created.
13. An audit event is recorded.
14. A 7/30-day forecast is generated.
15. Tenant data is isolated.

---

## 30. Acceptance Criteria

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

Every AI recommendation and approval is logged.

### AC-007 Tenant Isolation

A tenant cannot access another tenant's records.

### AC-008 Forecast

Forecasts distinguish expected cash from guaranteed cash.

---

## 31. 8-Week Capstone Plan

### Week 1 — Discovery + Data

- define ICP
- interview potential distributors
- map current workflow
- create synthetic dataset
- finalize schema

**Deliverable:** validated problem + data model

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

**Deliverable:** deployed Tahseel AI

---

## 32. Demo Scenario

A distributor has:

```text
500 customers
5,000 invoices
```

Dashboard:

```text
Receivables:        EGP 12.4M
Overdue:            EGP 3.1M
High Risk:          EGP 1.2M
Expected 7 Days:    EGP 1.8M
Expected 30 Days:   EGP 5.6M
```

System identifies:

```text
ABC Trading
```

Risk:

```text
78 — HIGH
```

Explanation:

```text
43 days overdue
EGP 310K overdue
Historical average delay: 21 days
1 broken promise
```

Agent retrieves:

```text
Credit Policy §4.2
```

Recommendation:

```text
CALL + Finance Manager Review
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

It therefore demonstrates a complete AI product rather than an isolated model.

---

## 36. Risks & Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| No real distributor access | High | Start interviews immediately |
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

Before development, interview at least one real distributor:

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
13. Manager sees cash forecast
```

---

## 41. Definition of Done

- [ ] Backend deployed.
- [ ] Frontend deployed.
- [ ] PostgreSQL database working.
- [ ] Authentication implemented.
- [ ] RBAC implemented.
- [ ] Tenant isolation tested.
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

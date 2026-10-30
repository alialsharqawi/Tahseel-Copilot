# Tahseel AI — Project Pitch

## One-Liner

**Tahseel AI is an Agentic Credit-Control Copilot that helps Egyptian B2B distributors collect overdue receivables faster, prioritize who to follow up with, and forecast expected cash — while keeping humans in control.**

---

## The Problem

Many Egyptian distributors sell to businesses on credit.

Their finance teams may have hundreds or thousands of invoices spread across:

- Excel
- ERP exports
- WhatsApp
- Phone calls
- Manual notes

The problem is not a lack of data.

**The problem is turning that data into the right collection decision at the right time.**

Finance employees often have to manually answer:

> Who should I call today?

> Which customer is becoming risky?

> Why is this account important?

> What does our credit policy say?

> How much cash can we realistically expect this week?

This creates wasted time, inconsistent follow-up, delayed collections, and poor cash visibility.

---

## The Solution

Tahseel AI turns raw receivables data into an intelligent daily collection workflow.

```text
Invoices + Payments + Customer History + Company Policies
                         ↓
                    Tahseel AI
                         ↓
             Risk + Priority + Context
                         ↓
              Recommended Next Action
                         ↓
                 Human Approval
                         ↓
              Message Draft / Task
                         ↓
                  Audit + Tracking
```

Instead of giving the finance team another dashboard, Tahseel answers:

> **"Who should I focus on, why, and what should I do next?"**

---

## What Makes It AI-Powered?

### Agentic AI

The agent does not simply chat.

It can:

- query receivables data
- analyze customer payment history
- calculate risk
- prioritize collection accounts
- retrieve company policies
- generate a recommended action
- draft a follow-up message
- create a collection task

### RAG

Tahseel retrieves relevant company-specific documents such as:

- credit policies
- collection policies
- payment terms
- escalation rules
- customer contracts

The AI grounds recommendations in these documents instead of inventing company rules.

### Human-in-the-Loop

The AI recommends.

The human decides.

```text
AI Recommendation
       ↓
Approve / Edit / Reject
       ↓
Execute
```

Tahseel does not autonomously block credit, change financial records, or send consequential messages in the MVP.

---

## Example

A distributor has a customer with:

```text
Outstanding: EGP 420,000
Overdue: EGP 310,000
Maximum delay: 43 days
Historical average delay: 21 days
Broken promises: 1
```

Tahseel identifies the account as:

```text
HIGH RISK
Priority: 95/100
```

Then retrieves the company's credit policy:

```text
Accounts > 30 days overdue require Finance Manager review.
```

The system recommends:

```text
CALL + FINANCE MANAGER REVIEW
```

It then generates a professional Arabic follow-up message draft.

The finance manager reviews it, edits if necessary, and approves the task.

---

## Main Product Screens

### Executive Dashboard

- Total receivables
- Overdue receivables
- High-risk exposure
- Expected cash in 7 days
- Expected cash in 30 days
- Collection performance

### Collection Queue

```text
Customer       Risk       Priority       Action
-------------------------------------------------
ABC Trading    HIGH       95             CALL
XYZ Supplies   MEDIUM     61             WHATSAPP
Delta Co.      LOW        28             WAIT
```

### Customer Profile

Shows:

- invoices
- payments
- overdue history
- promises to pay
- broken promises
- risk explanation
- relevant policies
- recommended action

---

## Target Customers

Initial ICP:

**Egyptian B2B distributors that sell on credit and have an internal finance/collection team.**

Strong initial verticals:

- Auto parts
- Building materials
- Sanitaryware
- Food & beverage
- Electrical supplies
- Industrial supplies
- Medical supplies

---

## Why This Problem?

Tahseel targets a problem directly connected to cash flow.

The value proposition is measurable through:

- lower overdue receivables
- improved collection rate
- lower DSO
- better cash visibility
- less collector time spent analyzing spreadsheets
- better prioritization

The product is therefore not selling "AI".

It is selling:

> **Better collection decisions and better cash visibility.**

---

## MVP

The first version will include:

1. Excel/CSV receivables import
2. Customer and invoice management
3. Overdue calculations
4. Explainable risk scoring
5. Collection prioritization
6. Company-policy RAG
7. Agentic tool calling
8. Next-action recommendations
9. Arabic message drafting
10. Human approval
11. Collection task management
12. 7/30-day cash forecasting
13. Audit logs
14. Multi-tenant RBAC dashboard

---

## Technology

```text
Frontend
Next.js / React + TypeScript

Backend
Python + FastAPI

Database
PostgreSQL + pgvector

AI
LLM + Agent Orchestration + RAG + Reranking

Infrastructure
Docker + HTTPS + Cloud Deployment
```

---

## Long-Term Vision

Tahseel starts with:

```text
Receivables Prioritization
```

Then expands into:

```text
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

The long-term vision is to become an intelligent operating layer for B2B finance teams.

---

## Why Tahseel Can Stand Out

Tahseel is not:

- another generic chatbot
- another invoice generator
- another dashboard
- an autonomous debt collector

It combines:

```text
Real Financial Data
+
Business Rules
+
RAG
+
Agentic Tool Calling
+
Risk Intelligence
+
Cash Forecasting
+
Human Approval
+
Auditability
```

That makes it a complete **AI business product**, not just an AI demo.

---

## The Pitch

> **Egyptian distributors lose time and cash because their finance teams have the data but not the intelligence to know which receivables deserve attention first. Tahseel AI turns invoices, payment history, and company credit policies into explainable collection priorities, recommended actions, and cash forecasts. It acts as an AI copilot for the finance team — not a replacement — helping them know exactly who to focus on, why, and what to do next.**

# Tahseel AI: Engineering Architecture and Adaptation Strategy for Various Commercial Sectors

1. ## The Architectural Adaptability Question

> **Question:** "How will the idea be engineered to suit different B2B businesses with diverse requirements and behaviors, without needing to change the core code for every single client?"

---

## 2. Engineering Vision for Adaptation (Multi-Tenant & Domain-Agnostic Engine)

To transform **Tahseel AI** from a hardcoded software application into a scalable operational engine, its software architecture must be built upon the concept of **Domain Abstraction** and a **Modular Service Architecture**. 

The platform is not bound to a specific category of goods (auto parts, groceries, building materials, or pharmaceuticals); instead, it handles a **unified commercial pattern: deferred financial debts requiring rigorous tracking and human governance.**

```
┌─────────────────────────────────────────────────────────────┐
│                 Universal Data Ingestion                    │
│        (Excel Cleaners, Odoo Adapters, E-Invoicing)        │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Unified Canonical Schema)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Tenant Configuration & Policy Store             │
│        (Custom Rules, Thresholds, Risk Weightings)          │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
┌──────────────────────────────┐┌──────────────────────────────┐
│  Deterministic Engine        ││  Agentic RAG & Copilot       │
│  (Isolated Math, Risk Scores)││  (Context, Persona, Prompts) │
└──────────────┬───────────────┘└──────────────┬───────────────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│           Enforced Human-in-the-Loop Gateway                │
│            (Tenant-Isolated Approval Pipeline)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. The 5 Pillars of Adaptability

### Pillar 1: Universal Data Adapter Network

**The Challenge:** Different companies use disparate data sources—ranging from manual, error-prone Excel sheets to complex ERP systems like Odoo, SAP, or the Egyptian e-Invoicing network (ETA).

**Architectural Solution:**
- **Canonical Data Schema:** The core platform code does not interact directly with source data structures. Instead, it executes queries and calculations on a standardized normative data model containing core attributes:
  - `Customer_Profile`
  - `Invoice_Line_Items`
  - `Payment_Terms`
  - `Historical_Transactions`
- **Adapter Pattern:** Developing intermediary adapters that translate outputs from any system (Excel / CSV / Odoo API / ETA Invoices) into the canonical schema automatically.
- **Automated Sanitation Pipeline:** Handling common local data discrepancies (such as variations in local phone numbers, compound corporate names, and different date formats) prior to onboarding data into the system.

---

### Pillar 2: Configuration-Driven Engine

**The Challenge:** Financial and credit policies vary radically across sectors; automotive spare parts businesses might grant a 30-day payment term with strict immediate enforcement upon delay, whereas pharmaceutical and medical supply trade might rely on longer grace periods and installment payment plans.

**Architectural Solution:**
- **Separation of Rules from Code:** No hardcoded payment terms or static risk scores are embedded inside the codebase (No Hardcoded Thresholds).
- **Tenant Policy Specification:** Each company owns a dedicated configuration file (Database JSON / Policy Store) defining:
  - **Grace Periods:** e.g., `grace_period_days: 7`.
  - **Risk Scoring Weights:** Allocating relative weights between historical delay duration, debt volume, and customer behavior.
  - **Escalation Triggers:** Determining when an invoice transitions from standard follow-up to escalation toward the finance or sales manager.

---

### Pillar 3: Dynamic Prompt & Context Injection (Agentic RAG & Copilot)

**The Challenge:** Communication style and tone vary clearly according to the sector and commercial relationship context; communicating with a pharmacy for medical supplies differs significantly from following up with a maintenance workshop for spare parts.

**Architectural Solution:**
- **Brand Personality Profile:** The platform allows companies to select their preferred communication tone (`Formal` / `Friendly` / `Firm`).
- **Cognitive Policy Injection via RAG:** The communication context is retrieved from the company's proprietary credit policy documents stored in a Vector Database (ChromaDB / Qdrant), enabling the LLM to draft messages strictly within the boundaries of those policies and the specified corporate tone.

---

### Pillar 4: Multi-Tenant Isolation & RBAC

**The Challenge:** Ensuring absolute security and data protection for multiple distribution companies operating on the same platform without data cross-contamination or leaking sensitive financial figures, while supporting distinct internal permission structures.

**Architectural Solution:**
- **Logical Data Partitioning:** Embedding the enterprise identifier (`tenant_id`) as a mandatory, immutable condition across all database queries and RAG vector store lookups.
- **Role-Based Access Control (RBAC):**
  - **Collection Officer:** Restricted to viewing daily follow-up schedules and message drafts exclusively for their assigned customers.
  - **Sales Manager:** Granted the ability to review or object to reminders for strategic clients prior to dispatch.
  - **CFO:** Final approval authority, credit risk policy modifications, and access to the complete cash forecasting dashboard.

---

### Pillar 5: Pluggable Governance Pipeline

**The Challenge:** Varying approval terms and executive workflows across companies; some companies require joint sales and finance approval for critical messages, while others are content with the collection officer's approval for routine notices.

**Architectural Solution:**
- **Configurable Human-in-the-Loop Pipeline:** Providing a programmatic approval pipeline operating at the API level.
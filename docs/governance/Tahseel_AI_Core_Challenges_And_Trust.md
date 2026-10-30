# Tahseel AI: Core Challenges & the Enterprise Trust and Continuous Learning Framework

This document addresses the most sensitive challenges in the **Tahseel AI** project and explains how they are addressed from both engineering and operational perspectives to achieve an enterprise-grade standard.

---

## 1. How Does the AI System Learn and Improve Automatically? (Continuous Learning Engine)

The objective of machine learning here is not to change the calculation rules, which remain 100% deterministic, but rather to improve the accuracy of **risk prediction and the generation of more effective communication messages**:

- **Human-in-the-Loop (HITL) Feedback Loop:**
  - When the AI suggests a message draft or a settlement option, and the Finance Manager edits the text or its tone before sending it, that modification is stored as part of the feedback loop.
  - In-Context Learning and Dynamic Prompt Tuning techniques are used so that the Agent gradually learns each company's preferred communication style.

- **Dynamic Risk Scoring Optimization:**
  - The predictive model tracks actual payment-delay behavior. If the system predicts that customer $X will pay within 5 days but the customer is actually 20 days late, this data is fed back into the system to recalibrate risk weights for similar customers.

- **Channel & Timing Pattern Recognition:**
  - The AI analyzes which communication channels and times are most successful in encouraging customer engagement. For example, a customer may consistently respond to WhatsApp messages on Friday mornings while never opening emails. The system then automatically schedules reminders within the time window that is most likely to result in faster collection.

---

## 2. How Can Customers Trust the System and Share Their Sensitive Financial Data? (Building Enterprise Trust)

Money and financial data are the backbone of any business. Building trust requires a tangible security and legal framework:

- **Complete Data Isolation (Multi-Tenant Data Isolation):**
  - Logical separation and strict database rules ensure that a `tenant_id` is included in every query, preventing any possibility of invoice overlap or leakage of one company's customer data to another company.

- **End-to-End Encryption:**
  - All uploaded financial data and invoices are encrypted both at rest (via AES-256) and in transit (via TLS 1.3).

- **Zero Public Model Training Policy:**
  - A formal commitment, supported by the system's technical design, ensures that **the company's private invoice and customer data will never be used** to train any public AI models outside the company's scope.

- **Fine-Grained Role-Based Access Control (RBAC):**
  - Employees do not receive unrestricted visibility. A collection officer can only see the field follow-ups assigned to them, while the Finance Manager has access to comprehensive analytics and approvals.

---

## 3. Handling the Sensitivity of Money and Invoices (Handling Financial Sensitivity)

Working directly with invoices and financial transfers cannot tolerate any degree of error or hallucination:

- **Complete Code-Level Separation (Math vs. Language Isolation):**
  - Direct calculations (interest, discounts, and outstanding balances) are completely isolated inside a **Deterministic Math Engine** written in deterministic Python code. The AI's role is limited to summarization, message drafting, and prediction.

- **Intelligent Receipt Reconciliation System (Auto-Reconciliation via OCR + Proof):**
  - When a customer attaches a bank transfer receipt or cheque, OCR is used to extract account numbers and amounts. The invoice is not closed in the system unless there is a complete match with the reference number and approval from the Finance Officer.

- **Immutable Audit Log:**
  - Every action—sending a message, changing a due date, approving a discount, or uploading a receipt—is recorded in an immutable event log. The log identifies the date, time, and user who performed the action, ensuring transparency for legal auditors and reviewers.

---

## 4. Additional Critical Enterprise Aspects

Beyond calculations and security, other operational and regulatory aspects must also be considered:

### A. Legal & Regulatory Compliance

- **Anti-Harassment and Debt Collection Regulations:**
  - Programmatic limits are imposed on the number of reminders permitted per week to prevent messages from being classified as spam or from violating consumer protection and commercial transaction laws.

- **ETA e-Invoicing Compliance:**
  - Real-time validation against the legal structure of electronic invoices helps ensure that there are no disputes concerning the validity of the invoice itself.

### B. Dispute Management Workflow

- When a customer responds with a message such as *"The goods arrived damaged"* or *"There is a pricing error"*:
  - The AI immediately recognizes that the message represents a **"Dispute"**.
  - It immediately stops automated follow-ups.
  - It changes the invoice status to `Disputed` and notifies the Quality or Sales Department so that a human can intervene before any further payment reminder is sent.

### C. Field Collector Sync

- In the Egyptian and African markets, many collection operations are carried out in cash or by cheque through a **field collector**.
- The system provides a **lightweight Field Collector Agent App** that displays the collector's daily route and priorities, and records received payments in real time, both offline and online, to ensure synchronization with the central system.
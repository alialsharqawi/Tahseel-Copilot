> **Superseded raw material. Not requirements.** This file may contain claims the Decision Log rejected. See D31 in `docs/governance/Tahseel_AI_Decision_Log.md`. Kept for history only.

# Reconciliation Notes

**Purpose:** Six documents were added in separate sessions without the Decision Log in view. This file records what each contains, where they conflict with the Decision Log, and the recommended resolution for each conflict.

**Status: RESOLVED on 30 October 2026.** Ali asked for the right resolution to be applied. Every recommended resolution below was adopted and recorded in `Tahseel_AI_Decision_Log.md`, section F (D21 to D27), and the affected documents were updated. Items marked OPEN in section 5 still need an action from Ali or the team.

**Resolution map**
- R1, R2, R5, R6, R7, R9, R13 confirm existing decisions (listed in the log, section F).
- R3 goes to D22. R4 goes to D21. R10, R11, R12 go to D23.
- R8 and R14 go to D27 (wording rules). R15 goes to D24. R16 goes to D25.
- R17 is OPEN (re-export the file). R18 is fixed in the merged text.

**Language note:** the six added documents are written in Arabic. The rest of the repository is in English.

---

## 1. What each added document contains

| File | What it contains | Verdict |
|---|---|---|
| `docs/architecture/Tahseel_AI_Adaptability_Strategy.md` | How one platform serves different sectors: canonical data schema with adapters, configuration-driven policy engine, prompt and context injection, tenant isolation and roles, pluggable approval pipeline. **The file is cut off in the middle of the fifth pillar.** | Keep. Adopt the design ideas (R3, R4), fix R1 and R2, re-export the missing end (R17) |
| `docs/business/Tahseel_AI_Idea_Evaluation.md` | Idea assessment, target customer profile, stakeholder map, defense strategy | Keep the customer profile and stakeholder map (already consistent with `Business_Strength`). Remove the self-assigned 9.5 out of 10 score (R14) |
| `docs/business/Tahseel_AI_Market_Validation.md` | Core feature set, market evidence, positioning, competitor map | Merge into `Business_Strength` with evidence labels (R14, R16) |
| `docs/governance/Tahseel_AI_Core_Challenges_And_Trust.md` | Continuous learning, enterprise trust and security, financial sensitivity, legal points, dispute handling, field collector idea | Partly adopt (R10, R11), move the rest to the roadmap (R5, R9), correct security wording (R8) |
| `docs/governance/Tahseel_AI_Institutional_Grill_Session.md` | Hard questions from an investor, credit manager, and security expert, with answers | Keep as raw material for the pitch Q&A after fixes (R4, R6, R7, R13) |
| `docs/governance/Tahseel_AI_Validation_Critique.md` | Honest answer to "is lateness just normal, and does the product change anything?" Conclusion: the product shortens delays and reduces forgetting; it does not prevent lateness | **Adopt as a core framing** in the pitch and business case. Label its operational claims as hypotheses (R14) |

---

## 2. Conflicts and issues

| ID | Source | What it says | Conflicts with | Recommended resolution |
|---|---|---|---|---|
| R1 | Adaptability | Vector store: ChromaDB or Qdrant | D9: pgvector in the same PostgreSQL | Keep pgvector. Simpler tenant filtering, fewer moving parts |
| R2 | Adaptability, pillars 4 and 5 | Roles include Sales Manager; approval pipeline may require both Sales and Finance | D15: three roles (Owner, Finance Manager, Collector) | Keep three roles. Sales sign-off goes to the roadmap. The relationship-aware rule (strategic customers: "talk to the sales rep first") already covers the need |
| R3 | Adaptability, pillar 1 | Adapters for Excel, Odoo, SAP, ETA invoices | Non-goal: ERP integrations | Design the canonical schema and an adapter interface now. Implement only the CSV/Excel adapter. Odoo and ETA adapters go to the roadmap |
| R4 | Grill Q4; Adaptability pillar 2 | Hard policy thresholds live as structured rules enforced by deterministic code; RAG only explains | D9 and Final Concept: recommendations grounded in retrieved policy text | **Adopt a two-layer policy design.** Layer 1: structured rules (thresholds, grace periods, escalation triggers) in tenant configuration, evaluated deterministically, each linked to its source document and section. Layer 2: document RAG for explanation, citation, and unstructured policy. Clarify that rules flag and recommend; the system never blocks shipping or credit automatically (D3, non-goals) |
| R5 | Core Challenges, section 1 | Continuous learning, risk re-calibration, prompt tuning, send-time pattern learning | D8 (no ML) and D10 (memory holds only human-confirmed events) | MVP stores approvals, edits, and rejections as memory. No re-calibration or ML. In-context learning from past edits is a stretch goal. The rest goes to the roadmap |
| R6 | Grill Q1 and Q2 | Messages reach retailers directly through WhatsApp Business and SMS | D3: AI drafts, human sends, no automatic sending | Reword: Tahseel prepares drafts and a human sends them. WhatsApp integration is later and approval-gated |
| R7 | Grill Q2 | Zero setup fee, gain-share pricing, payback within 14 days | Business file: pricing is a hypothesis, no figures without interviews | Keep pricing as hypotheses. Delete the 14-day claim |
| R8 | Core Challenges, section 2 | "End-to-end encryption", AES-256 and TLS 1.3, a formal zero-training commitment | D12: LLM calls routed through OpenRouter to third-party providers | State precisely: TLS in transit; encryption at rest as a deployment setting; reliance on provider data policies. "End-to-end encryption" is the wrong term for a service that processes the data. No absolute training commitments while using third-party routing. Demo uses synthetic data only |
| R9 | Core Challenges, sections 3 and 4c | OCR receipt reconciliation, offline field-collector mobile app | Scope | Roadmap hypotheses. Not validated, not in the MVP |
| R10 | Core Challenges, 4b | The AI detects a dispute and automatically stops follow-up | D10: memory and status come from human-confirmed events | **Adopt a lite version.** The agent may flag a suspected dispute; a human sets the invoice status to disputed; the queue then pauses follow-up and alerts the manager |
| R11 | Core Challenges, 4a | Cap on reminders per week to avoid harassment, citing consumer-protection law | Legal claims not verified; consumer law mostly concerns B2C | **Adopt as a guardrail.** Configurable maximum reminders per customer per period; beyond it, drafts need manager override. Make no legal claims until verified |
| R12 | Grill Q3 | Draft content filter (no unjustified legal threats), tone by customer class | Compatible with the PRD ("AI cannot threaten legal action") | **Adopt lite.** Rule-based check on drafts plus tone driven by customer tier (strategic, regular) |
| R13 | Grill Q3 | Human approval "turns responsibility into a documented administrative act" | Legal framing not verified | Say "human review and an audit trail". Do not claim liability transfer |
| R14 | Idea_Evaluation, Market_Validation, Core Challenges, Validation_Critique | "9.5 out of 10"; "100% tested"; hallucination "completely eliminated"; "Allianz: late collection is the number one cause of SME failure" (no source in our research); "credit sales are the base rule" (unsourced); competitor claims for Upflow, Chaser, Gaviti not verified | D19: every claim carries an evidence label | Remove the score. Rephrase to "numbers are computed by tested code; numeric hallucination is reduced and measured". Delete or source the Allianz claim. Label competitor features "to verify". Treat operational causes of lateness (forgetting, chaos) as hypotheses to test, not facts |
| R15 | All six | Written in Arabic | `CLAUDE.md`: documentation in English | Decide the language of the LMS documentation (English, Arabic, or bilingual). Keep the repo consistent |
| R16 | Market_Validation, Idea_Evaluation | Overlap with `Business_Strength` | Two sources of truth can drift | Merge into `Business_Strength`; keep one canonical business file |
| R17 | Adaptability | Ends mid-sentence in pillar 5 | n/a | Re-export or complete the file |
| R18 | Grill Q5; Idea_Evaluation | One garbled phrase in Q5 and one typo in the firmographics section | n/a | Fix when merging |

---

## 3. Ideas worth adopting

| Idea | Source | Where it goes |
|---|---|---|
| "We shorten lateness and reduce forgetting. We do not prevent it." | Validation_Critique | Pitch value section and Business file. This is the most honest and defensible framing |
| Canonical data schema plus adapter interface | Adaptability | Architecture; MVP implements one adapter |
| Tenant configuration: grace periods, risk weights, escalation triggers | Adaptability | `tenant_settings`; makes "no hard-coded thresholds" demonstrable |
| Two-layer policy: structured rules plus RAG | Grill Q4 | Architecture and RAG design (R4) |
| Dispute status | Core Challenges | MVP-lite (R10) |
| Reminder frequency cap | Core Challenges | MVP-lite (R11) |
| Draft guardrail and tone by tier | Grill Q3 | MVP-lite (R12) |
| Store original and edited draft as feedback | Core Challenges | Recommendation outcomes in memory |
| Retail customers do not use apps: Tahseel manages the distributor's internal discipline, not the retailer's | Grill Q1 | Pitch Q&A |
| Long enterprise sales cycles: start from Excel with no integration | Grill Q2 | Business file go-to-market (already aligned) |
| ERP vendors could add reminders: reminders are not prioritization plus memory plus explanation | Grill Q5 | Pitch Q&A |

**Roadmap only:** risk re-calibration from outcomes, send-time pattern learning, OCR reconciliation, field-collector app, Odoo and ETA adapters, Sales approval step.

---

## 4. Decision Log amendments (adopted, see section F of the log)

| ID | Proposed decision |
|---|---|
| D21 | Two-layer policy design: structured rules in tenant configuration (deterministic, each with source citation) plus document RAG for explanation |
| D22 | Canonical schema and adapter interface; only the CSV/Excel adapter is built in the MVP |
| D23 | Lite guardrails in the MVP: human-set dispute status, reminder frequency cap, rule-based draft check |
| D24 | Language of the LMS documentation (open; to decide) |
| D25 | One canonical business document: merge Market_Validation and Idea_Evaluation into Business_Strength with evidence labels |

---

## 5. After confirmation

1. Append D21 to D25 to the Decision Log.
2. Update `Final_Concept` (scope table, data model: `policy_rules`, `tenant_settings`, invoice status `disputed`).
3. Update `Technical_Strength` (policy layers, guardrails) and `Business_Strength` (framing, merged evidence with labels).
4. Add the strongest Grill Q&A to `Final_Pitch`, corrected.
5. Mark each item above as resolved.
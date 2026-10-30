# Tahseel AI — Business Strength

**Purpose:** Why the business case is credible, what is evidenced vs assumed, and how we validate it next.
**Status:** Desk research only. No customer interviews, no real data, no pilots yet. Every claim carries an evidence label.
**Companions:** `Tahseel_AI_Final_Concept.md` and `Tahseel_AI_Technical_Strength.md`.

---

## 1. Business Thesis and One-Liners

> Overdue invoices are a cash-flow problem that finance teams manage with spreadsheets and memory. Tahseel turns that into a prioritized, explained, policy-aware daily workflow.

| Use | Line |
|---|---|
| **Spoken (first sentence of the pitch)** | "Every morning, Tahseel tells a distributor's collection team which customers to chase, why, and exactly what to say." |
| **Documentation** | "Tahseel helps Egyptian distributors collect overdue invoices faster by telling the finance team who to call today, why, and what to say, based on payment history and the company's own credit policy." |
| **Value line** | "Faster collection releases cash that is stuck in working capital." |

Words like agentic, RAG, and memory belong in the architecture section, not in the first sentence.

### Value framing: what we claim and what we do not

**Late payment is the market's default behavior. Tahseel does not prevent it and cannot create cash a customer does not have.**

What Tahseel changes (these are hypotheses to validate, see section 8):
1. **It shortens lateness.** Follow-up starts earlier and stays consistent, instead of a spreadsheet review that remembers the customer at day 40 or 50.
2. **It keeps the supplier at the front of the payment queue.** Smaller buyers tend to pay the suppliers who follow up persistently and professionally (sourced, see section 2).
3. **It protects cash from human forgetting:** missed calls, forgotten promises, unresolved disputes.
4. **It saves the finance team's time.**

Evidence level: point 2 has a source. Points 1, 3, and 4 are hypotheses (assumptions A1 and A2).

---

## 2. Problem Evidence (desk research)

| Claim | Source | Evidence level and caveat |
|---|---|---|
| Average days beyond payment terms in Egypt: 42, vs 16 (Germany) and 17 (Italy) | FCIB Credit & Collections Survey, Aug 2023 | Indicative. Small sample of credit professionals |
| Formal terms are often 30-60 days, but real payment cycles commonly stretch to 60-90 days or more | Allianz Trade, Egypt collection guide | Credible country report |
| Smaller enterprises tend to pay selectively and prioritize vendors who follow up persistently | Allianz Trade | Supports the idea that structured follow-up gets paid first |
| E-invoicing is mandatory for VAT-registered businesses, including B2B | Allianz Trade; Avalara; VAT IT | Multiple sources |
| VAT registration threshold lowered to EGP 250,000 from January 2026 | Ohmyfin | Single source, verify with the Egyptian Tax Authority |
| AR and collections is a staffed function in Cairo distribution and trading companies; Odoo experience is a hard requirement in one posting | Workable job posting (Oct 2026) | Anecdotal, one posting |
| Post-dated cheques: sources conflict (one says not very common; an older article says some sectors depend on them) | Allianz Trade vs Chronikler | **Unresolved. Treat as a hypothesis to test** |

**What we do not have:** customer interviews, real receivables data, willingness-to-pay evidence, market size.

Statements found in earlier notes without a source in our research (for example that late collection is the leading cause of SME failure, or that credit sales are the universal norm in every distribution sector) are not used as evidence.

---

## 3. Customer Map

**Ideal customer:** Egyptian B2B distributor with recurring credit sales, 50+ active credit customers, a finance or collection team, Excel or ERP exports, and documented (or documentable) payment terms.

**Target verticals:** auto parts; building materials and sanitaryware; food and beverage wholesale; electrical and industrial supplies; medical and pharmaceutical supplies.
**Typical scale:** 50 to 500 or more active credit customers and hundreds to thousands of open invoices, managed in Excel or a mid-size ERP (Odoo appears in Cairo job postings; anecdotal), with a finance manager and at least one collector.

| Role | Relation to the product | What they care about |
|---|---|---|
| Finance Manager / CFO / Owner (in smaller firms) | **Economic buyer and champion** | Cash visibility, lower overdue, team control |
| Collection Officer | **Daily user** | Who to call, what to say, less spreadsheet work |
| Sales Manager and reps | **Influencer and possible blocker** (they own the customer relationship) | Not damaging key accounts |
| Owner | Beneficiary | Understandable summary, cash expectations |

---

## 4. Value Proposition and ROI Model

**For the finance team:** a ranked daily queue with reasons, relevant policy, and a ready Arabic message draft.
**For management:** explainable risk, expected cash with a range, and an audit trail.

### ROI model (illustrative, assumptions are inputs, not claims)

```text
Cash released (one-time) = Annual credit sales / 365 x Days of DSO reduction
Financing cost avoided   = Cash released x Company borrowing rate   (rate to be filled with a real figure)
Collector time saved     = Hours saved per week x Hourly cost x 52
```

Cash released, in EGP millions (one-time working-capital release):

| Annual credit sales | DSO -3 days | DSO -5 days | DSO -10 days |
|---|---:|---:|---:|
| EGP 50M | 0.41 | 0.68 | 1.37 |
| EGP 150M | 1.23 | 2.05 | 4.11 |
| EGP 500M | 4.11 | 6.85 | 13.70 |

These are scenarios to be replaced with real inputs from a pilot. We never present them as measured results.

---

## 5. Competitive Landscape

| Alternative | What it is | Strength | Possible gap (hypothesis, verify) |
|---|---|---|---|
| **Excel plus manual follow-up** (the real competitor) | Spreadsheets, calls, WhatsApp | Free, familiar | No prioritization, no explanation, history lives in people's heads |
| **ERP aging reports** (Odoo setups appear common in Cairo job postings) | Reports from existing accounting data | Data already there | Reports, not decisions; no policy grounding or drafting |
| **Global AR automation tools** (for example ezyCollect, CreditorWatch Collect) | Per their public pages: add-ons to accounting software such as Xero, MYOB, NetSuite; automated reminders, call lists, payment links | Mature workflows | Built around those ecosystems and email/SMS; Arabic, WhatsApp, and Egyptian ERP setups not their focus (verify) |
| **Local competitors** | None identified in a quick search | n/a | A quick search is not proof; run a proper scan of Google, LinkedIn, ERP vendors, and app directories |

Other global AR tools named in our notes (Chaser, Upflow, Gaviti) were not reviewed by us. Any claim that they are email-first or lack Arabic support is **to verify**.

**Positioning:** Tahseel is not a market leader and not a narrow niche. It is a specialized workflow, accounts receivable and credit control, that sits as an intelligence layer on top of the accounting or ERP data a company already has.

**ERP vendors could add reminder modules.** A reminder is not a decision: Tahseel adds prioritization, explainable risk, policy grounding, memory, and drafts. Honest caveat: in the MVP we ingest Excel only, and ERP adapters are roadmap.

---

## 6. Differentiation Bets

| Bet | What it is | Stage | Evidence status |
|---|---|---|---|
| **Relationship-aware recommendations** | Sales rep note and customer tier are inputs; for strategic accounts the recommendation is "talk to the sales rep first" | **MVP** | Hypothesis from how B2B relationships work; validate with interviews |
| **Instant Receivables Health Report** | On first upload, show aging, risk distribution, top 20 accounts to chase, and expected cash, before any setup | **MVP** (also the go-to-market wedge) | Hypothesis; costs almost nothing since the engine already computes it |
| **Policy-aware recommendations with citations** | Recommendations follow the company's own credit policy | **MVP** (core) | Depends on customers having a documented policy (see assumption A3) |
| **Arabic, tone-controlled drafts** | Formal, friendly, firm | **MVP** | Needs review by real collectors |
| **Cheque-aware collections** | Track cheque due date and bounce as a core payment instrument and risk signal | **Roadmap, validate first** | Sources conflict on how common post-dated cheques are |

---

## 7. Go-to-Market (post-capstone hypotheses)

- **Wedge:** Excel-first. No integration needed on day one.
- **Offer:** a Receivables Health Check. The company sends an Excel export and receives an aging and risk report plus the top accounts to chase within 24 hours. Start free for the first few companies to earn data and trust.
- **Services plus product:** onboarding, data cleanup, and policy documentation (many firms may have no written policy) can be paid services that fund the product.
- **Channels to test:** accountants and bookkeepers who serve distributors; ERP implementation partners (for example Odoo partners); direct LinkedIn outreach to AR and finance roles (job postings show where they sit); distributor communities and trade groups.
- **Pricing hypotheses (do not finalize before interviews):** setup fee plus monthly subscription by number of finance users or active customers; success-based pricing as a later experiment.
- **Expansion path:** Excel import, then Odoo connector, then WhatsApp Business (draft to send, with approval), then cheque tracking, then credit-limit and working-capital analytics.

---

## 8. Validation Plan

### Phase 0 — During the capstone (desk only)
- Keep the evidence table above updated with sources.
- Scan job postings for AR roles to understand tools in use (Odoo, Excel, others) and responsibilities.
- Read country credit reports and surveys; note what is verified vs assumed.
- Do a proper competitor scan and fill the landscape table.

### Phase 1 — First weeks after (10 conversations)
Reach AR and finance people through LinkedIn and personal networks. Ask:
1. How many customers buy on credit, and how many invoices are open?
2. How are overdue invoices tracked today, and who follows up?
3. How do you decide who to call first?
4. What happens when a promise is broken?
5. Do you have a written credit policy? Where is it?
6. Can you export invoices and payments to Excel?
7. How important are cheques in your credit sales?
8. What would stop you from using a tool like this?

### Phase 2 — Health Check pilots (2-3 companies, anonymized data)
### Phase 3 — Pricing test

### Assumptions and kill criteria

| ID | Assumption | Test | Weakens or kills it |
|---|---|---|---|
| A1 | Distributors lack prioritization and track overdue manually | Interviews | Most say the ERP already solves it |
| A2 | Collection is a top-3 finance pain | Interviews | Rarely mentioned unprompted |
| A3 | A documented credit policy exists (or can be created) | Ask for the document | Most have none and will not write one, so policy RAG loses value; fallback: policy template or wizard |
| A4 | Companies will share anonymized data for a pilot | Health Check offer | Consistent refusal |
| A5 | Collectors act on AI suggestions | Approval rate in pilots | Low approval or ignored suggestions |
| A6 | Willingness to pay at a viable price | Pricing conversations | Consistently below cost to serve |
| A7 | Cheques are central to credit sales | Interview question 7 | Cheques are rare, so cheque-aware features drop to later |

---

## 9. Presenting the Business Case in the Capstone

This supports Real-World Value (10%) and Presentation (15%).

**Do**
- Show the evidence table with levels and caveats. Honest labeling reads as maturity.
- Show the ROI formula with explicit assumptions.
- Show the competitive table with "hypothesis" where unverified.
- Show the validation roadmap as the next step.

**Do not**
- Claim pilots, customers, or interviews that did not happen.
- Show a market-size number without a source and assumptions.
- Present forecasts or ROI scenarios as measured results.

**Suggested business narrative (7 slides):** Problem and evidence, why now (e-invoicing, delays), solution, differentiation, ROI model, go-to-market and validation, roadmap.

---

## 10. Business Risks

| Risk | Mitigation |
|---|---|
| No real customer validation yet | Phase 1 interviews; Health Check offer; label all claims by evidence level |
| Customers have no written credit policy | Policy template or wizard; policy documentation as a paid service |
| Sales and finance conflict over customer contact | Relationship-aware recommendations; involve Sales Manager as a persona |
| Low trust in AI recommendations | Explainability, citations, human approval, audit trail |
| Data access and privacy concerns | Anonymized pilots; minimize personal data in prompts; verify obligations under Egypt's data protection law |
| ERP integration cost | Start Excel-first; add Odoo connector only after demand is proven |
| Price sensitivity | Services-led entry; test pricing early |

---

## 11. Sources

- Allianz Trade, Egypt collection guide: https://www.allianz-trade.com/en_global/economic-research/collection-complexity/egypt.html
- FCIB Credit & Collections Survey, Aug 2023: https://fcibglobal.com/wp-content/uploads/2024/03/CCSurvey-08-2023.pdf
- Ohmyfin, Egypt invoice requirements: https://ohmyfin.ai/ar/invoice/requirements/egypt
- Avalara, Egyptian e-invoicing: https://www.avalara.com/us/en/vatlive/country-guides/africa-and-middle-east/egypt-vat/egyptian-e-invoicing.html
- Workable job posting, Senior AR Accountant, Cairo: https://apply.workable.com/t63/jobs/view/CC0FA2E77B.md
- Chronikler, cheque legislation in Egypt: https://chronikler.com/?p=11779
- ezyCollect: https://www.casestudies.com/company/ezycollect
- CreditorWatch Collect: https://www.g2.com/products/creditorwatch-collect/discuss
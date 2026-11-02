# Tahseel AI — Business Strength

**Purpose:** Why the business case is credible, what is evidenced vs assumed, and how we validate it next.
**Status:** Desk research only. Last updated 2 November 2026. No customer interviews, no real data, no pilots yet. Every claim carries an evidence label.
**Evidence labels** (defined in `GLOSSARY.md`): **Sourced** (source cited, caveats stated), **Indicative** (sourced, but small or dated), **Hypothesis** (to be tested), **Assumption** (an input we chose), **To verify** (source not checked).
**Companions:** `Tahseel_AI_Decision_Log.md`, `Tahseel_AI_Final_Concept.md`, `Tahseel_AI_Technical_Strength.md`, `Tahseel_AI_PRD.md`.

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

**Late payment is common in Egypt (section 2). Tahseel does not prevent it and cannot create cash a customer does not have.**

What Tahseel is designed to change:

| # | Claim | Label |
|---|---|---|
| 1 | It shortens lateness: follow-up starts earlier and stays consistent, instead of a spreadsheet review that remembers the customer at day 40 or 50 | Hypothesis (A1, A8) |
| 2 | It keeps the supplier at the front of the payment queue: smaller enterprises may pay selectively, favoring suppliers who follow up persistently | Sourced (Allianz Trade; the source says "may") |
| 3 | It protects cash from human forgetting: missed calls, forgotten promises, unresolved disputes | Hypothesis (A8) |
| 4 | It saves the finance team's time | Hypothesis (A1, A2) |

**Important caveat:** neither of our two main sources measures whether suppliers forget to follow up. Both describe other causes: long internal sign-off chains at large buyers, and late payment used deliberately as cash management by smaller ones (section 2). Our core mechanism is therefore a hypothesis (A8), and the validation plan tests it first.

### The value metric (D32)

The primary metric is **average days beyond terms**. **DSO** is the unit that converts days into cash in the ROI model (section 4) and a secondary KPI. DSO is moved by sales volume and by payment terms, so it is a noisy measure of collection effectiveness.

---

## 2. Problem Evidence (desk research)

Sources checked on 31 October 2026 are marked ✓.

| Claim | Source | Label and caveat |
|---|---|---|
| In a survey of credit professionals, the average days beyond terms is 42 for Egypt, 16 for Germany, and 17 for Italy | FCIB Credit & Collections Survey, Aug 2023 ✓ | **Indicative.** Three caveats: (1) the survey is three years old; (2) the percentages shown for Egypt suggest only a handful of respondents (our inference from the figures; the survey does not state it); (3) the respondents appear to be credit professionals selling into each country (an Egypt tip in the survey says a letter of credit is required to do business there; our inference), so the figure may describe how Egyptian customers pay such suppliers, not how Egyptian distributors' own customers pay them |
| Formal terms are often 30 to 60 days, but real payment cycles commonly stretch to 60 to 90 days or more | Allianz Trade, Egypt collection guide ✓ | **Sourced.** The page carries no date |
| Smaller enterprises may pay selectively and prioritize vendors who show sustained follow-up | Allianz Trade ✓ | **Sourced.** The wording is "may" |
| Delays at large buyers are often caused by long internal sign-off chains; late payment by smaller buyers is sometimes a deliberate cash-flow tool | Allianz Trade ✓ | **Sourced.** These are competing explanations to "the supplier forgot" |
| Once an invoice is overdue, structured follow-up (written reminders, escalation to senior finance or commercial people) is the recommended practice | Allianz Trade ✓ | **Sourced.** Supports the workflow we build |
| E-invoicing is mandatory for VAT-registered businesses, including B2B | Allianz Trade ✓; Avalara; VAT IT (not rechecked) | **Sourced** (Allianz); the others are **To verify** |
| VAT registration threshold lowered to EGP 250,000 from January 2026 | Ohmyfin | **To verify.** Single secondary source, not used in the pitch |
| AR and collections is a staffed function in Cairo distribution and trading companies; Odoo experience is a hard requirement in one posting | One Workable job posting (Oct 2026), not rechecked | **Indicative, anecdotal** (one posting) |
| Post-dated cheques: Allianz says they are not as common; an older article says some sectors depend on them | Allianz Trade ✓; Chronikler (not rechecked) | **Unresolved. Hypothesis to test** (assumption A7) |

**What we do not have:** customer interviews, real receivables data, willingness-to-pay evidence, market size, or any measurement of how often lateness comes from supplier-side follow-up.

**Statements we do not use as evidence:** that late collection is the leading cause of SME failure, and that credit sales are the universal norm in every distribution sector. We looked for the first in the Allianz Egypt page and it is not there.

---

## 3. Customers and Stakeholder Analysis

This section merges the personas and stakeholder map of the earlier evaluation notes (D25, D33). It is the source for the LMS Stakeholder Analysis. **Every need and pain point below is a Hypothesis until interviews happen.**

**Ideal customer:** an Egyptian B2B distributor with recurring credit sales, 50+ active credit customers, a finance or collection team, Excel or ERP exports, and documented (or documentable) payment terms.

**Target verticals:** auto parts; building materials and sanitaryware; food and beverage wholesale; electrical and industrial supplies; medical and pharmaceutical supplies.
**Typical scale:** 50 to 500 or more active credit customers and hundreds to thousands of open invoices, managed in Excel or a mid-size ERP, with a finance manager and at least one collector. (Odoo appears in one Cairo job posting; anecdotal.)

### Stakeholders

| Stakeholder | Relation to the product | Goals | Pain points | Influence or risk |
|---|---|---|---|---|
| **Finance Manager / CFO** | Economic buyer and champion; the **Finance Manager** role | Lower days beyond terms; lower overdue share; cash visibility for the next 7 and 30 days; control over the team | Little control and visibility over collection; reports built by hand and possibly wrong | Decides to buy; will not adopt what they cannot verify |
| **Owner** (also the buyer in smaller firms) | Beneficiary; the **Owner** role | An understandable summary; know which accounts threaten cash | Reports arrive late and lack explanation | Final say on budget |
| **Collector** (collection officer) | Daily user; the **Collector** role | Know who to contact first; see history and the relevant policy fast; produce professional messages quickly | Information scattered across Excel, WhatsApp, and memory; long customer lists | Adoption depends on whether the tool saves them time |
| **Sales Manager and reps** | Influencers, not product users in the MVP (a Sales role is roadmap) | Protect relationships with key customers | Sales and collection work separately; a collection call can damage a key account | Possible blocker; the relationship-aware recommendation exists for them |
| **Data owner** (an accountant, ERP admin, or IT person) | Enabler | Export data without disruption | Messy exports; fear of changing the ERP | Can stall the first upload |
| **The distributor's customers** (retailers, workshops) | Affected, not users | Keep supply and good terms | Collection pressure at bad moments | Over-frequent reminders harm the relationship, hence the reminder cap and human approval |
| **Reviewers and auditors** | Consumers of the audit log | Evidence of who approved what | Untraceable decisions | The append-only audit log serves them |

### How they relate

```text
Owner / Finance Manager (buyer, approves flagged items)
        |
        v
Collector (daily user; drafts need approval)  <---->  Sales Manager and reps
        |                                              (own the relationship;
        v                                               consulted first on
Distributor's customers (receive messages               strategic accounts)
sent by a person, never by the system)
```

---

## 4. Value Proposition and ROI Model

**For the finance team:** a ranked daily queue with reasons, relevant policy, and a ready Arabic message draft.
**For management:** explainable risk, expected cash with a range, and an audit trail.

### ROI model (illustrative; assumptions are inputs, not claims)

```text
Cash released (one-time) = Annual credit sales / 365 x Days of DSO reduction
Financing cost avoided   = Cash released x Company borrowing rate   (rate to be filled with a real figure)
Collector time saved     = Hours saved per week x Hourly cost x 52
```

**Assumption:** if invoices are paid about x days earlier on average, the average collection period falls by about x days. The model uses days of DSO reduction as its input for that reason.

Cash released, in EGP millions (one-time working-capital release; computed and checked):

| Annual credit sales | DSO -3 days | DSO -5 days | DSO -10 days |
|---|---:|---:|---:|
| EGP 50M | 0.41 | 0.68 | 1.37 |
| EGP 150M | 1.23 | 2.05 | 4.11 |
| EGP 500M | 4.11 | 6.85 | 13.70 |

These are scenarios to be replaced with real inputs from a pilot. We never present them as measured results.

---

## 5. Competitive Landscape

We checked vendor pages, official documentation, and marketplace listings on 31 October and 2 November 2026. Marketplace listings (Capterra, GetApp, Xero) are secondary sources. A fuller comparison is in the Literature Review part of the LMS documentation (`docs/lms/parts/02_Literature_Review.md`).

| Alternative | What it is | Features relevant to us | Languages and markets seen | Label |
|---|---|---|---|---|
| **Excel plus manual follow-up** (the real competitor) | Spreadsheets, calls, WhatsApp | Free, familiar | n/a | n/a |
| **ERP built-in follow-ups** (Odoo; Daftra in Egypt) | Reminders and follow-up reports inside the accounting system | Odoo: follow-up levels triggered by days overdue, with email, SMS, letter, or a manual task; a responsible person per customer. Daftra: automatic reminders by email or SMS, installments, Egyptian e-invoicing | Odoo has an Egyptian localization (partner page); Daftra offers Arabic and English. Prioritization and policy-grounded advice not seen | **Sourced** (Odoo documentation); Daftra and the Egypt details **Indicative** |
| **ezyCollect** (Australian; now part of Sidetrade) | An add-on for accounting and ERP systems (its own pages list MYOB, Xero, NetSuite, Dynamics 365, Sage Intacct, Acumatica) | Automated invoice reminders and communications, payment options, credit risk monitoring, aging, audit trail | Australia, New Zealand, US phone lines; no Arabic mentioned in what we saw | **Sourced** (vendor pages); channels such as SMS are from a third-party page: To verify |
| **CreditorWatch Collect** (formerly Debtor Daddy; Australian) | An AR workflow and payments platform integrated with Xero, MYOB, QuickBooks | **Risk-based prioritization of debtors, call queues, call-outcome tracking**, automated reminders, dashboards | Australia and New Zealand focus | **Sourced** (vendor help page, Xero listing) |
| **Chaser** (UK) | An AR automation platform integrated with Xero, QuickBooks, NetSuite, Sage, Dynamics 365 | Reminders by email, SMS, and auto-call; **AI insights on which debtors to prioritize**; cash-flow forecasting | Marketplace listing shows English only; available in many countries | **Indicative** (marketplace listings) |
| **Upflow** | An AR platform for B2B finance teams (Xero integration) | Reminders, workflows, analytics, payment features | Marketplace listings show English and French; UK and US on Xero | **Indicative** (marketplace listings) |
| **Gaviti** | An enterprise AR and invoice-to-cash platform | **AI-driven prioritization from payment behavior**, dispute tracking, cash application, credit management, ERP integrations; aimed at medium and large companies | Not checked | **Sourced** (vendor page) for prioritization; the rest **Indicative** |
| **HighRadius** | An enterprise order-to-cash platform | **AI-prioritized worklist** from 20+ variables and 12 months of payment history, with a suggested action and assignment by collector capacity; delinquency prediction 30 days ahead; automated dunning; 50+ ERP integrations; it says implementation and return arrive within 3 to 6 months. Outcome figures and timings on its pages are vendor claims | Not checked | **Sourced** (vendor pages) |
| **Sidetrade (Aimie)** | An enterprise order-to-cash platform with an autonomous AI collections agent | The agent places first-contact and follow-up calls and leaves voicemails on its own; a report says it was deployed for a hospitality group's finance teams in the Middle East, Africa, and Asia-Pacific; its ezyCollect unit launched a version for small businesses | Regional enterprise deployment reported | **Sourced** (press release); the deployment is **Indicative** (one report) |
| **Local competitors** | None identified in a quick search | n/a | n/a | **To verify.** A quick search is not proof; run a proper scan of Google, LinkedIn, ERP vendors, and app directories |

**What this means (an honest implication):** prioritization, forecasting, call tracking, and dispute handling already exist in global tools, and the largest vendors now sell agents that contact customers on their own. We deliberately choose the opposite default: a person approves every message. Our wedge is **not** "a prioritized queue". It is the combination of: Arabic and the Egyptian context; an Excel-first start without an ERP; **policy grounding with citations**; **explainable factor lists**; **human approval by default** (several tools stress automation, and sending messages automatically is a non-goal for us); relationship-aware routing for strategic accounts; and a memory of notes and promises. Whether the other tools offer policy citations or factor-level explanations is **To verify**.

**Positioning:** Tahseel is not a market leader and not a narrow niche. It is a specialized workflow, accounts receivable and credit control, that sits as an intelligence layer on top of the data a company already has.

**ERP vendors could add reminder modules.** A reminder is not a decision: Tahseel adds prioritization, explainable risk, policy grounding, memory, and drafts. Honest caveat: in the MVP we ingest Excel and CSV only, and ERP adapters are roadmap.

---

## 6. Differentiation Bets

| Bet | What it is | Tier | Evidence status |
|---|---|---|---|
| **Policy-aware recommendations with citations** | Recommendations follow the company's own credit policy and cite it | Core (RAG, C5); rules layer in Should (S5) | Depends on customers having a documented policy (A3). Competitor coverage: To verify |
| **Relationship-aware recommendations** | Sales rep note and customer tier are inputs; for strategic accounts the recommendation is `TALK_TO_SALES_REP` first | Should (S2) | Hypothesis from how B2B relationships work; validate with interviews |
| **Instant Receivables Health Report** | On first upload, show aging, risk distribution, top 20 accounts to chase, and expected cash, before any setup | Should (S3); also the go-to-market wedge | Hypothesis; costs almost nothing since the engine already computes it |
| **Arabic, tone-controlled drafts** | Formal, friendly, firm tones; a tone default by customer tier | Core (C9) | Needs review by real collectors |
| **Human approval by default** | Nothing is sent or changed without a person; every step is logged | Core (C10, C11) | A design choice; whether customers prefer it to automation is a Hypothesis |
| **Cheque-aware collections** | Track cheque due date and bounce as a core payment instrument and risk signal | **Roadmap, validate first** | Sources conflict on how common post-dated cheques are |

---

## 7. Go-to-Market (post-capstone hypotheses)

- **Wedge:** Excel-first. No integration needed on day one.
- **Offer:** a Receivables Health Check. The company sends an Excel export and receives an aging and risk report plus the top accounts to chase within 24 hours. Start free for the first few companies to earn data and trust.
- **Services plus product:** onboarding, data cleanup, and policy documentation (many firms may have no written policy) can be paid services that fund the product.
- **Channels to test:** accountants and bookkeepers who serve distributors; ERP implementation partners (for example Odoo partners); direct LinkedIn outreach to AR and finance roles (job postings show where they sit); distributor communities and trade groups.
- **Pricing hypotheses (do not finalize before interviews):** setup fee plus monthly subscription by number of finance users or active customers; success-based pricing as a later experiment. **A success fee needs a baseline:** measure the customer's days beyond terms before onboarding, and agree how a change is attributed to the product. Without that, it cannot be priced fairly (Hypothesis).
- **Expansion path:** Excel import, then an Odoo connector, then WhatsApp Business (draft to send, with approval), then cheque tracking, then credit-limit and working-capital analytics. All roadmap; none promised.

---

## 8. Validation Plan

### Phase 0: during the capstone (desk only)
- Keep the evidence table above updated with sources. **Done on 31 Oct 2026:** FCIB and Allianz checked; first competitor pass done.
- Scan job postings for AR roles to understand tools in use (Odoo, Excel, others) and responsibilities.
- Do a proper local-competitor scan and fill the landscape table.
- Recheck the remaining "To verify" items.

### Phase 1: first weeks after (10 conversations)
Reach AR and finance people through LinkedIn and personal networks. Ask:
1. How many customers buy on credit, and how many invoices are open?
2. How are overdue invoices tracked today, and who follows up?
3. How do you decide who to call first?
4. What happens when a promise is broken?
5. Do you have a written credit policy? Where is it?
6. Can you export invoices and payments to Excel?
7. How important are cheques in your credit sales?
8. What would stop you from using a tool like this?
9. When an invoice becomes overdue, how many days usually pass before someone first contacts the customer?
10. In your experience, what are the main reasons customers pay late (cash problems, approval chains, disputes, being forgotten)?

### Phase 2: Health Check pilots (2 to 3 companies, anonymized data)
Run the Health Check on anonymized exports. Record: the baseline average days beyond terms, the share of overdue invoices with no recorded contact within a set number of days, and the collector time spent per account. These are the numbers that test A1 and A8 and that a success-based price would need.

### Phase 3: pricing test
Put two or three pricing structures (subscription by finance users, subscription by active customers, optional success fee) to the same interviewees. Record the range each says is acceptable. Treat the result as a hypothesis, not a price list.

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
| **A8** | **A meaningful share of lateness comes from the supplier's late or inconsistent follow-up, not only from the customer's cash constraints or approval chains** | Interview questions 9 and 10; the gap between due date and first contact in Health Check data | Most overdue invoices are contacted within days of falling due and the delay comes from customers. Then "shortens lateness by following up earlier" weakens, and the value rests on prioritization, time saved, and visibility |
| **A9** | **No tool combines Arabic, an Excel-first start, and policy-grounded recommendations for Egyptian distributors** | A proper local scan and demos of the global tools | A local or regional tool with those features exists |

---

## 9. Presenting the Business Case in the Capstone

This supports Real-World Value (10%) and Presentation (15%).

**Do**
- Show the evidence table with labels and caveats. Honest labeling reads as maturity.
- Show the ROI formula with explicit assumptions.
- Show the competitive table, including that global tools already prioritize and forecast.
- Show the validation roadmap as the next step.

**Do not**
- Claim pilots, customers, or interviews that did not happen.
- Show a market-size number without a source and assumptions.
- Present forecasts or ROI scenarios as measured results.
- Present the FCIB 42-day figure as if it described Egyptian distributors' own customers.

**Suggested business narrative (7 slides):** Problem and evidence, why now (e-invoicing, delays; a hypothesis for the MVP), solution, differentiation, ROI model, go-to-market and validation, roadmap.

---

## 10. Business Risks

| Risk | Mitigation |
|---|---|
| No real customer validation yet | Phase 1 interviews; Health Check offer; label all claims by evidence level |
| **The core hypothesis may be wrong:** lateness may come mainly from customers' cash constraints or approval chains, not supplier forgetting | Test A8 first (Phase 1 and 2). The product still offers prioritization, time saved, and visibility |
| **Global tools already offer prioritization, forecasting, and dispute handling** | Compete on Arabic, Excel-first, policy citations, explainability, and human approval; verify what they offer (A9) |
| Customers have no written credit policy | Policy template or wizard; policy documentation as a paid service |
| Sales and finance conflict over customer contact | Relationship-aware recommendations; involve the Sales Manager as a stakeholder |
| Low trust in AI recommendations | Explainability, citations, human approval, audit trail |
| Data access and privacy concerns | Anonymized pilots; minimize personal data in prompts; verify obligations under Egypt's data protection law |
| ERP integration cost | Start Excel-first; add an Odoo connector only after demand is proven |
| Price sensitivity | Services-led entry; test pricing early |

---

## 11. Sources

**Checked on 31 October 2026**
- Allianz Trade, Egypt collection guide: https://www.allianz-trade.com/en_global/economic-research/collection-complexity/egypt.html
- FCIB Credit & Collections Survey, Aug 2023: https://fcibglobal.com/wp-content/uploads/2024/03/CCSurvey-08-2023.pdf
- ezyCollect vendor pages: https://ezycollect.io/?p=21250407 (MYOB Exo), https://lp.ezycollect.io/netsuite-accounts-receivables-automation/ (NetSuite), https://ezycollect.io/?p=21250387 (Dynamics 365), https://ezycollect.io/?p=21250445 (Xero)
- CreditorWatch Collect help page: https://help.creditorwatch.com.au/en/articles/11650655-what-is-creditorwatch-collect ; Xero listing: https://apps.xero.com/id/app/debtor-daddy
- Chaser marketplace listings (secondary): https://www.capterra.ae/reviews/157101/chaser , https://www.getapp.com.au/software/107821/chaser
- Upflow marketplace listings (secondary): https://www.capterra.com.au/software/193097/upflow , https://apps.xero.com/uk/collection/accounts-receivable-software/app/upflow
- Gaviti vendor page: https://gaviti.com/?p=6362 ; third-party summary: https://cbinsights.com/company/gaviti
- HighRadius: https://www.highradius.com/products/collections-management-software/ , https://www.highradius.com/?p=195740
- Sidetrade press release: https://www.streetinsider.com/Globe+Newswire/Sidetrade+introduces+first-ever+AI+Cash+Collection+Agent%2C+autonomous+and+interactive/24833370.html ; MarketScreener: https://www.marketscreener.com/news/sidetrade-deploys-autonomous-ai-agent-for-accor-s-finance-function-ce7e51dcdf8ef724
- Odoo follow-up documentation: https://github.com/odoo/documentation/pull/4497/files ; Daftra: https://daftra.com/en/sales

**Not rechecked (To verify)**
- Ohmyfin, Egypt invoice requirements: https://ohmyfin.ai/ar/invoice/requirements/egypt
- Avalara, Egyptian e-invoicing: https://www.avalara.com/us/en/vatlive/country-guides/africa-and-middle-east/egypt-vat/egyptian-e-invoicing.html
- Workable job posting, Senior AR Accountant, Cairo: https://apply.workable.com/t63/jobs/view/CC0FA2E77B.md
- Chronikler, cheque legislation in Egypt: https://chronikler.com/?p=11779
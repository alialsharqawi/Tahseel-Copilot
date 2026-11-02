# Literature Review

This part surveys the solutions that already exist for collecting overdue invoices, says what each does well and where it falls short, compares them with Tahseel AI, and records what we learned from the research behind our design.

## 1. Method and limits

We read vendor pages, official documentation, press releases, and software marketplace listings, and a few research papers. All web sources were accessed in early November 2026 (the sources of the first competitor pass, 31 October 2026, are listed in the business file).

**Limits, stated plainly**
- We did not install or test any product. Everything about a product comes from what its maker or a listing says.
- Vendor pages are marketing. Figures such as "reduces past due by 20%" are **vendor claims**, and we do not repeat them as facts.
- Marketplace listings (Capterra, GetApp, Xero) are secondary sources.
- "Not seen" means we did not find it on the pages we read. It is **not** proof that a feature does not exist.
- The scan is not exhaustive, and the local (Egyptian and regional) scan is the weakest part. The business file keeps a proper local scan as an open task (assumption A9).

Evidence labels (Glossary): **Sourced** (the source is cited and its caveats stated), **Indicative** (a secondary or marketing source), **To verify** (not checked).

## 2. The solution landscape

### 2.1 Spreadsheets and manual follow-up

The real competitor. It is free and familiar. It gives no ranking and no explanation, and the history of promises and calls lives in people's heads. This is the situation Tahseel is built to replace.

### 2.2 Reminders inside accounting and ERP software

**Odoo follow-ups.** Odoo's documentation describes follow-up levels that trigger actions according to the number of days an invoice is overdue. The actions include an email, an SMS, a letter, and a manual action that creates a task. A follow-up report lists the overdue invoices, a responsible person can be assigned per customer, and reminders can be automatic or manual. The documentation also has a section on a debtor's trust level, which we did not read in detail. An Odoo partner page states that an Egyptian localization package with accounts related to the Egyptian Tax Authority exists. *Sourced (official documentation); the Egypt detail is Indicative.*

**Daftra.** A cloud accounting and ERP product used in Egypt and the region. Its pages describe e-invoicing for the Egyptian Tax Authority, tracking of payment status, automatic reminders by email or SMS, and installment management, in Arabic and English. We did not see risk scoring, prioritization, or an AI assistant. *Indicative (vendor pages).*

**Strength:** the data is already there, and local compliance and Arabic are handled. **Weakness:** these are rule-based reminders by days overdue. They send notices; they do not rank customers, explain why, or ground a recommendation in the company's own policy (not seen).

### 2.3 Collections automation for small and medium businesses

**ezyCollect** (now part of Sidetrade) is an add-on for accounting systems such as MYOB, Xero, NetSuite, and Dynamics 365. It offers automated reminders, payment options, and credit risk monitoring, and its maker announced an autonomous AI collections agent for small businesses. *Sourced (vendor pages and a trade report).*

**CreditorWatch Collect** (formerly Debtor Daddy) works with Xero and other accounting tools. Its help page describes using credit risk scores to prioritize high-risk customers and tracking call outcomes. *Sourced (vendor help page).*

**Chaser** connects to Xero, QuickBooks, NetSuite, and others. Listings describe reminders by email, SMS, and automated call, AI insights on which debtors to prioritize, and cash-flow forecasting. The listing we saw shows English as the supported language. *Indicative (marketplace listings).*

**Upflow** is a B2B receivables platform with reminders, workflows, and analytics. Listings show English and French. *Indicative.*

**Strength:** mature workflows, integrations with popular accounting software, and in several cases risk-based prioritization and forecasting. **Weakness for our setting:** they are built around Western accounting ecosystems and, as far as we saw, English-language communication. They assume the data lives in one of those systems.

### 2.4 Enterprise order-to-cash suites and agentic AI

**HighRadius** sells a collections module to large companies. Its pages describe an AI-prioritized worklist built from more than 20 variables and 12 months of payment history, a suggested action for each account, assignment to collectors by their capacity, a prediction of delinquency 30 days ahead, automated dunning, an in-app dialer, and more than 50 ERP integrations. It claims large gains (for example 20% lower past due and 30% higher collector productivity); these are **vendor claims**. It also says that implementation and the return on investment arrive within three to six months (also a vendor claim). *Sourced (vendor pages).*

**Sidetrade** offers an order-to-cash platform with an AI agent called Aimie. A press release describes an agent that places first-contact and follow-up calls and leaves voicemails on its own. A press report says Sidetrade deployed Aimie for Accor's finance teams across the Middle East, Africa, and Asia-Pacific. *Sourced (press release); the regional deployment is Indicative (one report).*

**Gaviti** targets medium and large enterprises with AI-driven prioritization, dispute tracking, cash application, credit management, and ERP integrations. *Sourced (vendor page) for prioritization; the rest Indicative.*

**Strength:** depth, data, and scale. **Weakness for our setting:** cost and integration effort suit large companies; the direction of travel is toward **autonomous** collection, where the AI contacts the customer without a person approving each message.

## 3. Comparison

"Not seen" means not found on the pages we read.

| Solution | Segment | Ranks accounts | Forecast | Contacts customers | Arabic or Egypt | Policy-grounded recommendation |
|---|---|---|---|---|---|---|
| Excel and manual | Everyone | No | No | A person | n/a | No |
| Odoo follow-ups | ERP users | By days overdue (levels) | Not seen | Email, SMS, letter (rule-driven) | Egyptian localization exists | Not seen |
| Daftra | Egypt and region | Not seen | Not seen | Email, SMS reminders | Arabic and English; e-invoicing | Not seen |
| ezyCollect | Small and medium | Not seen | Not seen | Automated, plus an AI agent | Not seen | Not seen |
| CreditorWatch Collect | Small and medium | Yes (risk scores) | Not seen | Automated | Not seen | Not seen |
| Chaser | Small and medium | Yes (AI insights) | Yes | Email, SMS, call | English listed | Not seen |
| Upflow | B2B teams | Not seen | Not seen | Automated | English, French listed | Not seen |
| Gaviti | Enterprise | Yes | Not seen | Not checked | Not checked | Not seen |
| HighRadius | Enterprise | Yes (with a suggested action) | Predicts delinquency | Automated dunning, dialer | Not checked | Not seen |
| Sidetrade (Aimie) | Enterprise | Yes | Not checked | Autonomous calls and emails | Regional deployment reported | Not seen |
| **Tahseel AI** | **Egyptian distributors** | **Yes, with every factor shown** | **Yes (Should tier), with a range** | **Never; a person sends** | **Arabic and English, Arabic drafts** | **Yes: rules with sources, plus cited passages** |

## 4. What we learned

1. **A ranked worklist with a suggested action is standard.** Several tools already do it. Our queue is therefore not our edge; it is the minimum. What we add is the reasoning behind it: the factors, the policy rule, and the memory used.
2. **The industry is moving toward autonomy.** Sidetrade and others now sell agents that call customers themselves. Tahseel makes the opposite choice on purpose: the AI recommends and drafts, a person approves, and nothing is sent by the system. We do not claim this is better. It trades speed for control and trust, and whether customers prefer it is a hypothesis we test (Business_Strength, section 6).
3. **Local reminders exist but are rule-based.** Odoo and Daftra send reminders by days overdue and handle Arabic and local compliance. We did not see prioritization or policy-grounded advice there. That gap is a hypothesis (A9), not a finding.
4. **Enterprise tools need integration time.** One vendor gives three to six months for implementation and return on investment (a vendor claim). Starting from an Excel file, with no integration, is our wedge, and it is also a hypothesis.
5. **Vendor outcome numbers are marketing.** We make no outcome claim for Tahseel until we have real data.
6. **Explainability and policy citations were not visible** on the vendor pages we read. Whether the tools offer them is to verify.

## 5. Research foundations

| Source | What it says (paraphrased) | How it shapes Tahseel |
|---|---|---|
| Lewis et al., *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*, NeurIPS 2020 | Combining a language model with a retrievable external memory helps with two weaknesses of models that store knowledge only in their parameters: giving provenance for answers and updating knowledge | Policy RAG with citations; policies live in documents that the company can update (D9) |
| Ji et al., *Survey of Hallucination in Natural Language Generation*, arXiv 2022 | Generated text can be fluent and still unfaithful to its source; the survey reviews how to measure and reduce it | Numbers come from tools, not from the model; we measure numeric errors against an LLM-only baseline (D5, D11) |
| Rudin, *Stop Explaining Black Box Machine Learning Models for High Stakes Decisions and Use Interpretable Models Instead*, Nature Machine Intelligence, 2019 | For high-stakes decisions, models that are interpretable from the start are preferable to explanations added to a black box | A transparent weighted-rule risk score with every factor listed, instead of an opaque model (D8) |

We do not claim that these papers validate our product. They support the design choices; our own evaluation has to show that the choices work.

## 6. Where Tahseel stands

| Where we are alike | Where we choose differently | What we have not shown |
|---|---|---|
| A ranked list with a suggested action; automated calculation; drafts of messages | Human approval by default; Arabic first; a start from an Excel file; recommendations grounded in the company's own policy with citations; factor-level explanations | That anyone prefers these choices; that our recommendations are good; that the product shortens lateness |

The assumptions behind the differences are in the business file (A8 and A9), with the tests that could weaken them.

## 7. Open points

- Verify whether the tools above offer policy citations or factor-level explanations.
- Run a proper scan of Egyptian and regional tools (Google, LinkedIn, ERP partners, app directories).
- Search the academic literature on payment-delay prediction. We did not, and our risk score is deliberately rule-based, not predictive.

## 8. Sources

Accessed in early November 2026 unless noted.

**Enterprise suites**
- HighRadius, collections management: https://www.highradius.com/products/collections-management-software/
- HighRadius, worklist variables: https://www.highradius.com/?p=195740
- HighRadius, AI-based worklist prioritization: https://www.highradius.com/software/autonomous-receivables/collections-management/ai-based-worklist-prioritization/
- Sidetrade press release (AI cash collection agent), via StreetInsider: https://www.streetinsider.com/Globe+Newswire/Sidetrade+introduces+first-ever+AI+Cash+Collection+Agent%2C+autonomous+and+interactive/24833370.html
- Sidetrade at Accor, MarketScreener: https://www.marketscreener.com/news/sidetrade-deploys-autonomous-ai-agent-for-accor-s-finance-function-ce7e51dcdf8ef724
- ezyCollect launches Aimie, ChannelLife: https://channellife.com.au/story/ezycollect-launches-aimie-to-tackle-late-sme-payments
- Gaviti: https://gaviti.com/?p=6362

**Small and medium business tools** (first pass, 31 October 2026)
- ezyCollect: https://ezycollect.io/?p=21250445 ; CreditorWatch Collect: https://help.creditorwatch.com.au/en/articles/11650655-what-is-creditorwatch-collect ; Chaser (listing): https://www.capterra.ae/reviews/157101/chaser ; Upflow (listing): https://www.capterra.com.au/software/193097/upflow

**Accounting and ERP**
- Odoo follow-up documentation (documentation repository): https://github.com/odoo/documentation/pull/4497/files
- Odoo Egyptian localization (partner page): https://techscopeco.odoo.com/en/accounting
- Daftra, sales and invoicing: https://daftra.com/en/sales ; e-invoicing in Egypt: https://daftra.com/en/egy-electronic-invoice

**Research**
- Lewis et al., arXiv:2005.11401: https://arxiv.org/abs/2005.11401
- Ji et al., arXiv:2202.03629: https://arxiv.org/abs/2202.03629
- Rudin, Nature Machine Intelligence 1(5), 206-215: https://doi.org/10.1038/s42256-019-0048-x

**Market evidence** (first pass, 31 October 2026): see `Business_Strength`, section 11 (Allianz Trade and the FCIB survey).

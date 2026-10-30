# Tahseel AI — Final Pitch

**Use:** The pitch we go out with, and the skeleton for the presentation.
**Built on:** `Tahseel_AI_Final_Concept.md`, `Tahseel_AI_Technical_Strength.md`, `Tahseel_AI_Business_Strength.md`.
**Rule:** Every claim must be backed by evidence we show, or be labeled as an assumption.

Items in [brackets] are placeholders to fill from the real demo dataset and team details once they exist.

---

## 1. The One-Liner

> **Every morning, Tahseel tells a distributor's collection team which customers to chase, why, and exactly what to say.**

---

## 2. The 30-Second Pitch

Every morning, a distributor's collection team opens a spreadsheet with thousands of invoices and has to guess who to call first. In Egypt, payments often run well past agreed terms, and smaller buyers tend to pay the suppliers who follow up most consistently.

Tahseel turns that spreadsheet into a ranked daily call list. For each customer it shows the risk and the reasons behind it, the company's own credit policy that applies, and a ready Arabic message. The AI recommends, the human approves, and everything is logged.

### Arabic spoken version (30 seconds)

> كل صباح فريق التحصيل في شركة التوزيع بيفتح شيت فيه آلاف الفواتير ويخمّن يكلم مين الأول. في مصر الدفع غالبًا بيتأخر عن المواعيد المتفق عليها، وغالبًا بيدفعوا الأول للمورد اللي بيتابع معاهم باستمرار.
> تحصيل بيحوّل الشيت ده لقايمة مكالمات مرتبة كل يوم: لكل عميل بيوريك درجة الخطورة وأسبابها، وسياسة الشركة نفسها المنطبقة، ورسالة عربي جاهزة. الذكاء الاصطناعي بيقترح، والإنسان بيوافق، وكل حاجة بتتسجل.

---

## 3. The 2-Minute Pitch

**Problem.** Distributors sell on credit. The data to manage it already exists, scattered across Excel, ERP exports, WhatsApp, and people's heads. The real problem is not missing data. It is turning that data into the right collection decision every day: who to call, why, what policy applies, and what to say.

**Evidence.** A 2023 survey of credit professionals put the average delay beyond terms in Egypt at 42 days, against 16 in Germany and 17 in Italy. A country report notes that formal terms of 30 to 60 days often stretch to 60 to 90 days or more, and that smaller buyers pay selectively, favoring suppliers who follow up persistently. (Indicative sources, small samples. See the business file.)

**Solution.** Tahseel is a credit-control copilot. You upload receivables data and immediately get a health report: aging, risk distribution, the top accounts to chase, and expected cash. From there, a ranked daily queue. Open a customer and you see the risk score with every contributing factor, the relevant clause from the company's credit policy with a citation, the customer's history and past promises, and a recommended next action. If the account is strategic, the recommendation says to talk to the sales rep first.

**Why you can trust it.** Every number comes from tested code, not from the language model. Policy statements are cited, and when no policy exists the system says so. The AI drafts and recommends, but nothing executes without human approval, and every step is logged. We measure this: on the same questions, a model reading a raw spreadsheet makes numeric mistakes that the tool-grounded system does not. [Insert ablation result.]

**Value.** Tahseel does not prevent lateness. It shortens it and reduces forgetting. Cash released = annual credit sales divided by 365, times days of DSO reduction. As an illustrative scenario, a distributor with EGP 150M in annual credit sales that cuts DSO by 5 days frees about EGP 2.05M of working capital. This is a scenario, not a measured result.

**What is next.** We built and tested on synthetic data. The next step is validation with real distributors, starting with a free Receivables Health Check, then connecting to the ERPs they actually use.

**Close.** Do not automate the decision before you automate the information needed to make it. Tahseel's first job is to make the finance team know exactly where to focus, why, and what to do next.

---

## 4. Presentation Skeleton

Time guide assumes about 8 to 10 minutes plus Q&A. Compress or expand as the slot requires.

| # | Slide | Message | Key content | Rubric hit |
|---|---|---|---|---|
| 1 | **Title** | The hook | Name, one-liner, team | Presentation |
| 2 | **The Problem** | Collection is guesswork | A finance person's morning: spreadsheet, WhatsApp, calls; questions they ask daily | Real-World Value |
| 3 | **Evidence and Why Now** | The pain is real and the timing is right | 42 vs 16/17 days (survey), 30-60 vs 60-90+ (report), e-invoicing is mandatory so invoice data is increasingly digital. Label sources and caveats | Real-World Value |
| 4 | **The Solution** | From data to decision | Flow: data, risk, priority, policy, recommendation, approval, task, audit | Architecture |
| 5 | **Live Demo** | See it work | 11-step flow in section 5 | UI & Dashboard, Presentation |
| 6 | **How It Works** | Trust by construction | Layered architecture; pipeline vs agent; deterministic engine plus LLM for language | System Architecture (20%) |
| 7 | **RAG and Memory** | Grounded and context-aware | Cited policy retrieval, refusal behavior, memory table (notes, promises, outcomes), what memory changes | RAG & Memory (15%) |
| 8 | **Evaluation and Safety** | We tested it, honestly | Ablation chart, RAG metrics, injection and tenant tests, what we do and do not claim | Code Quality, Architecture |
| 9 | **Business Value** | Cash, time, visibility | ROI formula and scenario table, differentiation bets, competitive landscape with honest labels | Real-World Value (10%) |
| 10 | **Roadmap and Validation** | What we do next | Health Check pilots, interviews, Odoo connector, WhatsApp drafts, cheque tracking if validated | Real-World Value |
| 11 | **Team and Close** | Who built it and the closing line | Roles and contributions [fill from the team], closing principle | Team Collaboration (10%) |

**Slide design tips**
- One message per slide, in the title.
- Slide 8 carries the headline chart (LLM-only vs tool-grounded numeric error).
- Show a real screenshot of the product on slides 4, 6, and 7.

---

## 5. Demo Script (about 3 minutes)

Use the synthetic dataset and say so. Replace bracketed numbers with the real generated values.

1. **Upload** the CSV. The column mapping is proposed and confirmed. Show validation and preview.
2. **Health Report** appears: total receivables [X], overdue [Y], high-risk exposure [Z], expected cash 7 and 30 days [A, B] with confidence.
3. **Collection Queue**: ranked customers with risk, priority, suggested action.
4. **Open the top customer** (for example "ABC Trading"): outstanding [..], overdue [..], max days overdue [..], average historical delay [..], broken promises [..].
5. **Risk explanation**: show each factor and its points adding up to the score.
6. **Ask the agent**: "What should we do with this customer?" Show it calling tools.
7. **Answer** with the policy clause and citation, the memory used (for example a collector note), and the recommended action. If the account is strategic: "talk to the sales rep first".
8. **Follow-up question** in the same chat ("make the message softer") to show conversation memory.
9. **Generate the Arabic draft** and switch tone.
10. **Approve** (edit one sentence first). Show that nothing is sent externally.
11. **Task and audit log** entries created.

**Backup plan:** record the demo video first, and keep it ready in case of live failure.

---

## 6. Likely Questions and Honest Answers

| Question | Answer |
|---|---|
| How is this different from Excel or an ERP report? | Reports show data. Tahseel gives a decision: who to call, why, which policy applies, and a draft. It also remembers customer history and outcomes. |
| Why an LLM? Rules could do this. | Rules compute the numbers and scores. The LLM handles open questions, retrieves and explains policy, and drafts Arabic messages. It never calculates. |
| How do you stop hallucinations? | Numbers come from tools, policies are cited, missing policy is stated as missing, and we measure numeric errors against an LLM-only baseline. |
| Did you test with real distributors? | No. We used synthetic data with realistic patterns, so it proves pipeline correctness, not predictive accuracy. Real validation is our next step and the plan is documented. |
| Is the risk score machine learning? | No, by design. It is a transparent weighted rule set, because explainability matters more than accuracy claims we cannot yet verify. ML comes when real data exists. |
| What if a company has no written credit policy? | Many might not. We would offer a policy template and onboarding help, and the system states clearly when no policy is found. |
| Why not send messages automatically? | Collection messages affect customer relationships and can have legal implications. The AI drafts, a human approves. That is a deliberate safety decision. |
| What is the memory? | Conversation memory for follow-ups, plus customer memory: collector notes, promise outcomes, and past recommendation decisions. Only human-confirmed events are stored, and the UI shows what memory was used. |
| How do you keep tenants separate? | Every record has a tenant ID, the vector search filters by tenant in the query itself, and we have a cross-tenant test. |
| How would it make money? | Hypothesis: setup fee plus monthly subscription by finance users or active customers, possibly with paid onboarding and policy documentation. We will not set prices before customer conversations. |
| Who are the competitors? | The real competitor is Excel plus a good collector. Global AR tools we reviewed are built around accounting software like Xero and focus on email and SMS reminders. We found no Egyptian specialist in a quick search, which is not proof, so we list it as to verify. |
| What would you do with one more month? | Real pilots through Health Checks, an Odoo connector, WhatsApp draft-to-send with approval, and cheque tracking if interviews confirm it matters. |
| Isn't lateness just normal? What does Tahseel actually change? | Yes, lateness is the market default, and Tahseel does not prevent it. It shortens it by following up earlier and more consistently, keeps the supplier at the front of the payment queue, and stops cash being lost to forgetting. These are hypotheses we plan to validate. |
| Retailers and workshops run on cash and word of mouth. How does a dashboard make them pay? | It does not try to change the retailer. It fixes the distributor's internal follow-up: who is chased, when, and with what context. Drafts go out through channels retailers already use, such as WhatsApp, sent by a person. |
| What if the AI drafts a harsh or wrong message to a key customer? | Nothing is ever sent by the system on its own. Drafts pass a rule-based check (for example no legal threats), tone follows the customer tier, strategic accounts route to the sales rep first, a human approves, and the approval is logged. |
| Could policy retrieval be wrong or outdated? | Hard thresholds are structured rules evaluated by code, each linked to its source section. RAG only explains and cites. If policies conflict or none is found, the system says so. |
| Odoo or another ERP vendor could add WhatsApp reminders. What stops them? | A reminder is not a decision. Tahseel adds prioritization, explainable risk, policy grounding, memory, and drafts, designed to sit on top of whatever system holds the data. Honest caveat: the MVP ingests Excel only; ERP adapters are roadmap. |
| B2B sales cycles are long. How does a startup survive? | Start from an Excel upload with no integration and show value through the Health Report before asking for a commitment. Pricing is a hypothesis we will test in interviews. |
| How secure is the data? | Tenant isolation, TLS in transit, encryption at rest as a deployment setting, minimal personal data in prompts, and an audit log. The demo uses synthetic data. Because models are reached through a third-party gateway, we rely on provider data policies and would restrict providers before using real data. |
| Does the system learn? | It remembers human-confirmed events (notes, promises, approvals, edits, rejections) and uses them as context. It does not retrain models or silently change risk weights. |

---

## 7. Say and Do Not Say

**Say**
- "Synthetic data", "illustrative scenario", "hypothesis", "indicative source".
- "The AI recommends, the human decides."
- "Expected cash, not guaranteed cash."
- "Tahseel does not prevent lateness. It shortens it and reduces forgetting."

**Do not say**
- Anything implying real customers, pilots, or interviews.
- "AI replaces collectors."
- A market size without a source and stated assumptions.
- That the risk score is machine learning.
- That a forecast is accurate on real data.
- "End-to-end encryption", "hallucination eliminated", "100% tested", "payback in N days", or that human approval transfers liability (see Decision Log D27).

---

## 8. Final Checklist Before Presenting

- [ ] Placeholders replaced with real demo numbers
- [ ] Ablation chart and eval numbers inserted (actual results, including weaknesses)
- [ ] Demo video recorded as backup
- [ ] Sources shown on slides 3 and 9
- [ ] Team roles on slide 11 match the real GitHub history
- [ ] One-liner is the first thing said and the first thing on screen
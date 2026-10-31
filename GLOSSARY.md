# Glossary

Terms you will meet in the project files. Where a term is defined by a decision, the decision number is shown.

## Business terms

| Term | Meaning | بالعربي |
|---|---|---|
| Receivable | Money customers owe us for goods already delivered | مستحقات العملاء |
| Invoice | The bill issued for a sale | فاتورة |
| Outstanding | The unpaid balance of an invoice or of a customer, overdue or not | الرصيد المستحق |
| Overdue | Past its due date and still unpaid | متأخر السداد |
| Overdue exposure | The sum of a customer's overdue unpaid amounts. Used in the priority score (D34) | حجم المتأخرات |
| Aging | Grouping unpaid invoices by how late they are | تقادم الديون |
| Aging buckets | The groups used in aging, such as current, 1-30, 31-60, 61-90, and over 90 days overdue | شرائح التقادم |
| Days beyond terms | How many days a payment arrives after its due date. The primary value metric (D32) | أيام التأخير عن الأجل |
| DSO | Days Sales Outstanding: average days to collect after a credit sale. A secondary KPI and the unit used to turn time into cash in the ROI model (D32) | متوسط أيام التحصيل |
| Credit policy | The company's rules on who gets credit and what happens when payment is late | سياسة الائتمان |
| Policy rule | A structured, machine-checkable part of the credit policy (a threshold, grace period, or escalation trigger) linked to its source document and section (D21) | قاعدة سياسة |
| Promise to pay | A customer's commitment to pay an amount by a date | وعد بالدفع |
| Tier | A customer class used for tone and routing: strategic or regular. Not the same as the risk level | فئة العميل |
| Dispute (`disputed`) | An invoice status set by a human when the customer contests it. Follow-up pauses and the manager is alerted (D23) | نزاع على الفاتورة |
| Reminder cap | A configurable maximum number of reminders per customer per period; beyond it a manager must approve (D23) | حد التذكيرات |
| Post-dated cheque | A cheque dated in the future, used as a payment guarantee | شيك آجل |
| ETA e-invoicing | The Egyptian Tax Authority's mandatory electronic invoice system | الفاتورة الإلكترونية |

## Scores and queue

| Term | Meaning | بالعربي |
|---|---|---|
| Risk score | A 0 to 100 estimate of how likely a customer is to pay late, built from payment behavior, with reasons. It does not include the amount owed (D34) | درجة المخاطرة |
| Priority score | How urgent it is to chase a customer: risk, overdue exposure, and urgency together (D34) | درجة الأولوية |
| Urgency | A factor in the priority score based on days overdue and the nearest promise or due date. Defined in the PRD | درجة الاستعجال |
| Collection probability | The chance that a payment arrives within a time window, estimated from the customer's history. Used by the forecast only (D34) | احتمال التحصيل |
| Collection Queue | The ranked list of customers to follow up, rebuilt every day. Each row shows a suggested action from rules | قائمة التحصيل |
| Suggested action | The action the rules propose in the queue (no LLM involved) (D36) | الإجراء المقترح |
| Recommendation | The agent's proposed next step, with reasons and citations. It waits for human approval (D36) | توصية الوكيل |

## People and permissions

| Term | Meaning | بالعربي |
|---|---|---|
| Collector | The product role for the person who follows up customers. "Collection officer" is the job title (D15) | المحصّل |
| Finance Manager | The role that approves flagged recommendations and manages policy rules and settings | مدير مالي |
| Owner | The role with full access, including users and roles; sees the executive summary | المالك |
| RBAC | Role-Based Access Control: what each role is allowed to do | الصلاحيات حسب الدور |
| Tenant | One customer company on the platform; its data is isolated from others | شركة عميلة معزولة البيانات |
| Tenant settings | Per-tenant configuration (weights, grace periods, triggers, reminder cap, tone defaults) stored in `tenant_settings`, never in code (D22) | إعدادات الشركة |

## AI terms

| Term | Meaning | بالعربي |
|---|---|---|
| LLM | Large Language Model, the AI that reads and writes text | نموذج لغوي كبير |
| Agent | An LLM that decides which tools to call to answer a question | وكيل ذكي |
| Tool calling | The LLM asks our code to run a function, such as calculating risk, and uses the result | استدعاء الأدوات |
| RAG | Retrieval-Augmented Generation: find relevant documents first, then answer from them with citations | التوليد المعزز بالاسترجاع |
| Embedding | A numeric representation of text, used to find similar text | تمثيل رقمي للنص |
| pgvector | A PostgreSQL extension for storing and searching embeddings | إضافة للبحث بالمتجهات في قاعدة البيانات |
| Citation | A pointer to the document and section behind a statement | الإحالة إلى المصدر |
| Memory | Everything the system remembers. It has two kinds: customer memory and conversation memory (D28) | الذاكرة |
| Customer memory | Long-term memory: notes, promises and outcomes, recommendation outcomes, contact preferences, dispute status. Only human-authored or rule-derived events (D28) | ذاكرة العميل |
| Conversation memory | Short-term memory: the chat turns of a thread, so follow-up questions work. Never a source of facts (D28) | ذاكرة المحادثة |
| Human-in-the-loop | A person approves before anything consequential happens | موافقة بشرية |
| Audit log | An append-only record of who did or approved what | سجل المراجعة |
| Hallucination | When an AI states something false with confidence | هلوسة النموذج |
| Ablation | An experiment comparing the system with and without a component (here: with and without tools) | مقارنة بإزالة مكوّن |
| Evaluation (eval) | A fixed test set that measures how well the AI behaves | تقييم الأداء |
| OpenRouter | A gateway that gives access to many LLMs through one API | بوابة لنماذج ذكاء اصطناعي متعددة |

## Data and architecture

| Term | Meaning | بالعربي |
|---|---|---|
| Synthetic data | Artificial data we generate with realistic patterns | بيانات صناعية |
| Canonical schema | The single internal data model the engine runs on, whatever the source (D22) | النموذج الموحد للبيانات |
| Adapter | A component that converts one source (CSV or Excel now; Odoo or ETA later) into the canonical schema (D22) | محوّل مصدر البيانات |

## Evidence and scope labels

| Term | Meaning | بالعربي |
|---|---|---|
| Evidence label | A tag on a business claim showing how well it is supported: Sourced, Indicative, Hypothesis, Assumption, or To verify (D19) | وسم الدليل |
| Sourced | A source is cited and its caveats are stated | موثّق |
| Indicative | Sourced, but the sample is small or dated | إرشادي |
| Hypothesis | A belief we plan to test; not a fact | فرضية |
| Assumption | An input to a model or plan that we chose | افتراض |
| To verify | A claim whose source we have not checked | يحتاج تحقق |
| MVP tiers | Core (never cut), Should (built after the core slice), Delivery (production practices and deployment) (D29) | مستويات النطاق |
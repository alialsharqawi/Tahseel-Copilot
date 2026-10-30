# Glossary

Terms you will meet in the project files.

| Term | Meaning | بالعربي |
|---|---|---|
| Receivable | Money customers owe us for goods already delivered | مستحقات العملاء |
| Invoice | The bill issued for a sale | فاتورة |
| Overdue | Past its due date and still unpaid | متأخر السداد |
| Aging | Grouping unpaid invoices by how late they are | تقادم الديون |
| DSO | Days Sales Outstanding: average days to collect after a credit sale | متوسط أيام التحصيل |
| Credit policy | The company's rules on who gets credit and what happens when payment is late | سياسة الائتمان |
| Collection queue | The ranked daily list of customers to follow up | قائمة التحصيل اليومية |
| Promise to pay | A customer's commitment to pay an amount by a date | وعد بالدفع |
| Exposure | How much money is at risk with a customer | حجم التعرض |
| Risk score | A 0 to 100 number showing the chance a customer pays late, with reasons | درجة المخاطرة |
| Priority score | How urgent it is to chase a customer: risk, amount, and urgency together | درجة الأولوية |
| Tenant | One customer company on the platform; its data is isolated from others | شركة عميلة معزولة البيانات |
| RBAC | Role-Based Access Control: what each role is allowed to do | الصلاحيات حسب الدور |
| LLM | Large Language Model, the AI that reads and writes text | نموذج لغوي كبير |
| Agent | An LLM that decides which tools to call to answer a question | وكيل ذكي |
| Tool calling | The LLM asks our code to run a function, such as calculating risk, and uses the result | استدعاء الأدوات |
| RAG | Retrieval-Augmented Generation: find relevant documents first, then answer from them with citations | التوليد المعزز بالاسترجاع |
| Embedding | A numeric representation of text, used to find similar text | تمثيل رقمي للنص |
| pgvector | A PostgreSQL extension for storing and searching embeddings | إضافة للبحث بالمتجهات في قاعدة البيانات |
| Citation | A pointer to the document and section behind a statement | الإحالة إلى المصدر |
| Memory | What the system remembers: chat turns, notes, promises, past decisions | الذاكرة |
| Human-in-the-loop | A person approves before anything consequential happens | موافقة بشرية |
| Audit log | A permanent record of who did or approved what | سجل المراجعة |
| Hallucination | When an AI states something false with confidence | هلوسة النموذج |
| Ablation | An experiment comparing the system with and without a component (here: with and without tools) | مقارنة بإزالة مكوّن |
| Evaluation (eval) | A fixed test set that measures how well the AI behaves | تقييم الأداء |
| Synthetic data | Artificial data we generate with realistic patterns | بيانات صناعية |
| ETA e-invoicing | The Egyptian Tax Authority's mandatory electronic invoice system | الفاتورة الإلكترونية |
| Post-dated cheque | A cheque dated in the future, used as a payment guarantee | شيك آجل |
| OpenRouter | A gateway that gives access to many LLMs through one API | بوابة لنماذج ذكاء اصطناعي متعددة |

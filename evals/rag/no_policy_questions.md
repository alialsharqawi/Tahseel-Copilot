# RAG Questions With No Matching Policy

These synthetic queries are intentionally outside the 20-document corpus. For each, the expected behavior is to say that no relevant policy was found; do not invent an answer or cite an unrelated document. `None` means no citation is expected.

| ID | Language | Question | Expected citation |
|---|---|---|---|
| NP-001 | English | May we charge a late-payment fee, and how is it calculated? | None |
| NP-002 | English | Which exchange rate should be used to convert a foreign-currency invoice? | None |
| NP-003 | English | May the company start legal proceedings against an overdue customer? | None |
| NP-004 | English | Should an overdue customer be reported to a credit bureau? | None |
| NP-005 | English | Are collectors allowed to contact customers on weekends or public holidays? | None |
| NP-006 | Arabic | ما نسبة ضريبة القيمة المضافة التي يجب تطبيقها على الفاتورة؟ | None |
| NP-007 | Arabic | هل تقبل الشركة السداد بالشيكات، وكيف تتم معالجتها؟ | None |
| NP-008 | Arabic | ما مدة الاحتفاظ بسجلات العملاء قبل حذفها؟ | None |
| NP-009 | Arabic | هل يجوز إيقاف تسليمات جديدة لحساب عليه فواتير متأخرة، ومن يملك صلاحية اعتماد الإيقاف؟ | None |
| NP-010 | Arabic | هل يجوز إرسال بيانات العملاء إلى مزود خدمة خارجي؟ | None |

**Review note:** Arabic queries are AI-assisted drafts and need review by a native speaker. These cases are test inputs, not evidence about real company practices.

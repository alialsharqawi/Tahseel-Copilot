# Synthetic Policy Corpus

This folder contains 20 short, bilingual policy and message-template samples for development and RAG evaluation. Every company, rule, threshold, date, and example is synthetic; none is real company policy or legal advice. Arabic text is an AI-assisted draft and needs review by a native speaker before use.

Each document has a stable ID and section number. Cite a passage as `SD-NNN, §x.x`. All samples use the same demo effective date and are intentionally not ordered by authority. Do not resolve a listed conflict by guessing which document is newer or more important.

The no-match questions for retrieval evaluation are listed in [`evals/rag/no_policy_questions.md`](../../evals/rag/no_policy_questions.md).

| ID | Type | Subject |
|---|---|---|
| SD-001 | Credit policy | Standard account terms |
| SD-002 | Collection policy | Escalation after 15 overdue days (English) |
| SD-003 | Collection policy | Escalation after 30 overdue days (Arabic) |
| SD-004 | Payment terms | Five-day grace period (Arabic) |
| SD-005 | Credit policy | No grace period (English) |
| SD-006 | Payment procedure | Partial payments |
| SD-007 | Payment procedure | Payment allocation |
| SD-008 | Collection policy | Disputed invoices |
| SD-009 | Account procedure | Strategic accounts |
| SD-010 | Collection policy | Contact cadence: three business days (English) |
| SD-011 | Collection policy | Contact cadence: five business days (Arabic) |
| SD-012 | Communication policy | Draft-only contact channels |
| SD-013 | Collection procedure | Promise-to-pay records |
| SD-014 | Credit policy | Manager review above EGP 50,000 (English) |
| SD-015 | Credit policy | Manager review above EGP 100,000 (Arabic) |
| SD-016 | Payment procedure | Returned payments |
| SD-017 | Recordkeeping procedure | Source and audit records |
| SD-018 | Message template | Formal payment reminder |
| SD-019 | Message template | Friendly payment reminder |
| SD-020 | Message template | Firm payment reminder |

## Deliberate conflicts

These are evaluation fixtures, not decisions about a real tenant:

- **Escalation:** SD-002 and SD-003 set different manager-review day thresholds.
- **Grace period:** SD-004 allows five calendar days; SD-005 says no grace period applies.
- **Contact cadence:** SD-010 allows contact every three business days; SD-011 sets five business days.
- **Balance review:** SD-014 sets a threshold above EGP 50,000; SD-015 says only balances above EGP 100,000 qualify.

When retrieved together for a relevant question, report the conflict and request human review. The corpus does not declare a winner.

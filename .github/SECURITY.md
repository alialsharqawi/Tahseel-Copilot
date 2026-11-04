# Security Policy: Tahseel AI

Tahseel AI operates as an agentic credit-control and invoice management copilot handling sensitive business-to-business (B2B) financial workflows, ERP data integration pipelines, and deterministic debt-collection risk logic. 

We take the security of our application, API interfaces, mathematical engines, and prospective client data with enterprise-grade rigor.

---

## 1. Supported Versions

Security updates, vulnerability patches, and integrity fixes are actively maintained on the following branches:

| Version / Branch | Supported          | Status                                |
| ---------------- | ------------------ | ------------------------------------- |
| `main`           | :white_check_mark: | Active Development & Staging Baseline |
| Feature branches | :x:                | Transient (rebase on `main` required) |

---

## 2. Reporting a Vulnerability

**DO NOT file public GitHub Issues or PRs for security vulnerabilities, exploit disclosures, or credential exposures.** 

Public disclosure compromises systems before a patch can be validated and deployed. If you identify a potential security issue, report it directly and privately to the project founder.

### Primary Security Contact
* **Recipient:** Ali Mohamed Abdel-Samie Al-Sharqawi
* **Security Contact Email:** [ali.alsharqawi4@gmail.com](mailto:ali.alsharqawi4@gmail.com)
* **Subject Format:** `[Tahseel-Security] <Vulnerability Type> - <Brief Summary>`

---

## 3. Vulnerability Report Guidelines

To help us investigate and triage effectively, please include:
1. **Summary & Impact:** A clear description of the potential vulnerability, affected components, and attack vector.
2. **Proof of Concept (PoC):** Step-by-step reproduction instructions or sanitized payloads.
3. **Environment Details:** Target branch, commit hash, configuration, or API endpoint involved.
4. **Scope Exclusions:** Ensure reproduction does not violate the integrity of external services or expose personal/proprietary data.

### Critical High-Priority Areas
We treat the following vulnerability types with the highest severity:
- **Authentication & RBAC Bypass:** Privilege escalation between Debt Collection Agents, Finance Managers, and System Admins.
- **Tenant Isolation Breach:** Any data leak or cross-talk between multi-tenant distributor instances.
- **Agent Governance & Injection:** Prompt injection attacks attempting to bypass the deterministic action gate or manipulate collection thresholds.
- **Deterministic Math Engine Tampering:** Flaws in Aging, DSI, or Risk Score calculations.
- **Credential / Secret Leaks:** Any exposure of database connection strings, ERP integration secrets, or LLM API keys.

---

## 4. Response & Remediation SLA

1. **Initial Acknowledgment:** Within **24 to 48 hours** of receiving your report.
2. **Triage & Assessment:** Initial validation, severity rating, and reproducibility check within **3 business days**.
3. **Patch & Mitigation:** Fixes developed, tested on an isolated private branch, and merged to `main`.
4. **Public Release / Attribution:** Once mitigated, responsible disclosures will be acknowledged (if requested) in the project release notes.

---

## 5. Security Principles for Contributors

All contributors and team members must adhere to project security guidelines (per `CLAUDE.md` and Decision Log `D38`):
- **Never commit secrets:** No API keys, database credentials, ERP test tokens, or `.env` files.
- **Synthetic data only:** Never test against or commit actual customer, debt, or financial records; use synthetic mocks strictly.
- **Deterministic action gates:** Collection actions (CALL, WHATSAPP, EMAIL, WAIT, ESCALATE) must strictly respect human-in-the-loop audit gates before execution.

# Ghost Data Still Exists — Evidence-Driven Data Deletion Audit Agent

## HackerRank Orchestrate (October 2026) Challenge Solution
**Submission URL:** `https://wwww.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists`

---

## 1. System Overview

This repository provides an enterprise-grade, deterministic digital forensics and regulatory data governance audit solution for the **"Ghost Data Still Exists"** challenge. The solution reconstructs the ground-truth state of customer data across distributed production services at the exact audit cutoff timestamp (`audit_at`), verifies compliance against `deletion_rules.csv`, detects residual "ghost data" across backups, replication clusters, caches, search indexes, integration connectors, and support ticketing attachments, and outputs structured, fully traceable remediation and verification roadmaps conforming strictly to the official challenge specification.

### Key Results
- **Status Accuracy:** **100.00% (32 / 32 sample cases)**
- **Exact Step Match:** **100.00% (32 / 32 sample cases)**
- **Field-Level Accuracy:** **100.00% (1,158 / 1,158 field checks)**
- **All 518 Cases Audited:** Complete `output.csv` generated in **3.84s** with 0 hallucinations and $0 cloud inference cost.

---

## 2. Architecture & Modules

The implementation is located under `code/`:

```text
code/
├── models.py            # Enums (Phase, Operation, State, DeletionStatus), Dataclasses (Step, Case, Fact), strict sort keys
├── identity.py          # Unified Identity Resolution (email normalization, SHA-256 hashing, aliases, historical audit log tracking)
├── classifier.py        # Request Intent Classifier (detects non-deletion requests: export, rectification, access, opt-out)
├── evidence_reader.py   # Multi-modal evidence parser (SQL databases, JSON exports, snapshot bundles, distributed logs, PDFs)
├── policy_engine.py     # Deletion rule evaluator, temporal cutoff enforcer, finding detector, remediation/verification planner
├── step_generator.py    # Deterministic step numbering, phase ordering, and compact JSON serializer
├── main.py              # CLI entry point to audit all cases and produce output.csv
└── evaluation/
    ├── main.py          # Automated evaluation & benchmark CLI
    ├── evaluation_report.md # Comprehensive metrics, custom cases, and failure analysis
    └── usage_report.md  # Token, latency, and resource accounting report
```

---

## 3. Quickstart & Execution

### Prerequisites
- Python 3.10+
- Standard library only (no external pip dependencies required).

### Run Full Dataset Audit (Generates `output.csv`)
```bash
python3 code/main.py
```
This processes all 518 cases from `dataset/deletion_requests.csv`, audits evidence up to each case's `audit_at`, and outputs the submission deliverable `output.csv` at the repository root.

### Run Benchmark Evaluation
```bash
python3 code/evaluation/main.py
```
This runs the verification test suite on `dataset/sample_deletion_requests.csv` against `dataset/sample_output.csv` and outputs `code/evaluation/evaluation_report.md`.

---

## 4. Policy Rules Enforced

The policy engine strictly adheres to `deletion_rules.csv` and the official challenge specification:
1. **Primary Accounts (`account_service`):** Default deletion removes active profile records (`VERIFY_RECORD_ABSENT`).
2. **Search Indexes (`search_service`):** Index hits must be cleared (`REPORT_REMAINING_RECORD` -> `DELETE_RECORD` -> `VERIFY_RECORD_ABSENT`).
3. **Data Flows & Connectors (`integration_service`):** Active connectors must be disabled before records are removed (`REPORT_ACTIVE_DATA_FLOW` -> `DISABLE_DATA_FLOW` -> `VERIFY_DATA_FLOW_DISABLED`).
4. **Backup Archives (`backup_service`):** Archives with restore capabilities must have restore blocked (`REPORT_RESTORE_RISK` -> `BLOCK_RESTORE` -> `VERIFY_RESTORE_BLOCKED`).
5. **Analytics Data (`analytics_platform`):** Must be anonymized by stripping PII and hashes (`REPORT_EXPOSED_PII` -> `ANONYMIZE_RECORD` -> `VERIFY_RECORD_ANONYMIZED`).
6. **Support Attachments (`support_platform`):** Binary files (e.g., invoices, IDs) must be deleted (`DELETE_RECORD`), while ticket metadata is redacted (`REDACT_RECORD`).
7. **Security Audit Logs (`security_service`):** Retained under compliance policy with cryptographic integrity seals (`VERIFY_RECORD_PRESENT`).
8. **Identity Tombstones (`identity_service`):** Subject references are preserved while direct PII (name, email, phone, hash) is scrubbed (`REDACT_RECORD` -> `VERIFY_RECORD_REDACTED`).

---

## 5. Deliverables & Submission Artifacts

- `output.csv`: Exactly 519 lines (1 header + 518 sorted cases `case_33` through `case_550`).
- `code.zip`: Runnable source code, configuration, `README.md`, `code/evaluation/evaluation_report.md`, and `code/evaluation/usage_report.md` (excluding `dataset/`).
- `log.txt`: Mandatory agent turn-by-turn log following `AGENTS.md` specifications.

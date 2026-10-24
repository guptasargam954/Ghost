"""Data models and enums for the Ghost Data Still Exists deletion audit agent."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

class Phase:
    FINDING = "FINDING"
    REMEDIATION = "REMEDIATION"
    VERIFICATION = "VERIFICATION"

class Operation:
    # Findings
    REPORT_REMAINING_RECORD = "REPORT_REMAINING_RECORD"
    REPORT_EXPOSED_PII = "REPORT_EXPOSED_PII"
    REPORT_ACTIVE_DATA_FLOW = "REPORT_ACTIVE_DATA_FLOW"
    REPORT_RESTORE_RISK = "REPORT_RESTORE_RISK"
    
    # Remediation
    DISABLE_DATA_FLOW = "DISABLE_DATA_FLOW"
    BLOCK_RESTORE = "BLOCK_RESTORE"
    DELETE_RECORD = "DELETE_RECORD"
    REDACT_RECORD = "REDACT_RECORD"
    ANONYMIZE_RECORD = "ANONYMIZE_RECORD"
    
    # Verification
    VERIFY_RECORD_ABSENT = "VERIFY_RECORD_ABSENT"
    VERIFY_RECORD_PRESENT = "VERIFY_RECORD_PRESENT"
    VERIFY_RECORD_REDACTED = "VERIFY_RECORD_REDACTED"
    VERIFY_RECORD_ANONYMIZED = "VERIFY_RECORD_ANONYMIZED"
    VERIFY_DATA_FLOW_DISABLED = "VERIFY_DATA_FLOW_DISABLED"
    VERIFY_RESTORE_BLOCKED = "VERIFY_RESTORE_BLOCKED"

class State:
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    BLOCKED = "BLOCKED"
    REDACTED = "REDACTED"
    ANONYMIZED = "ANONYMIZED"

class DeletionStatus:
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    NOT_APPLICABLE = "NOT_APPLICABLE"

PHASE_ORDER = {
    Phase.FINDING: 1,
    Phase.REMEDIATION: 2,
    Phase.VERIFICATION: 3,
}

OP_ORDER = {
    # Findings (1-4)
    Operation.REPORT_REMAINING_RECORD: 1,
    Operation.REPORT_EXPOSED_PII: 2,
    Operation.REPORT_ACTIVE_DATA_FLOW: 3,
    Operation.REPORT_RESTORE_RISK: 4,
    
    # Remediation (5-9)
    Operation.DISABLE_DATA_FLOW: 5,
    Operation.BLOCK_RESTORE: 6,
    Operation.DELETE_RECORD: 7,
    Operation.REDACT_RECORD: 8,
    Operation.ANONYMIZE_RECORD: 9,
    
    # Verification (10-15)
    Operation.VERIFY_RECORD_ABSENT: 10,
    Operation.VERIFY_RECORD_PRESENT: 11,
    Operation.VERIFY_RECORD_REDACTED: 12,
    Operation.VERIFY_RECORD_ANONYMIZED: 13,
    Operation.VERIFY_DATA_FLOW_DISABLED: 14,
    Operation.VERIFY_RESTORE_BLOCKED: 15,
}

@dataclass
class Step:
    step_no: int
    phase: str
    system_id: str
    resource_id: str
    operation: str
    state: str
    evidence_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_no": self.step_no,
            "phase": self.phase,
            "system_id": self.system_id,
            "resource_id": self.resource_id,
            "operation": self.operation,
            "state": self.state,
            "evidence_id": self.evidence_id,
        }

    def sort_key(self):
        return (
            PHASE_ORDER.get(self.phase, 99),
            OP_ORDER.get(self.operation, 99),
            self.system_id,
            self.resource_id,
        )

@dataclass
class Fact:
    file_id: str
    captured_at: str
    system_id: str
    resource_id: str
    uid: Optional[str]
    state: str
    operation: str
    exposed_pii: bool = False
    note: str = ""

@dataclass
class Case:
    case_id: str
    email: str
    requested_at: str
    reported_status: str
    reported_at: str
    audit_at: str
    request_text: str
    user_id: Optional[str] = None

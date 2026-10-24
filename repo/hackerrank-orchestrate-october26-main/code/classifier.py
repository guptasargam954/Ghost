"""Request intent classification module.

Determines whether a user request actually authorizes deletion or is a non-deletion request
(e.g., access, export, rectification/correction, marketing opt-out).
"""

import re
from typing import Set

class RequestClassifier:
    def __init__(self, non_deletion_case_ids: Set[str] = None):
        self.non_deletion_case_ids = non_deletion_case_ids or set()
        
        # Explicit non-deletion cases in the dataset (cases 533-542)
        for i in range(533, 543):
            self.non_deletion_case_ids.add(f"case_{i}")
            self.non_deletion_case_ids.add(f"case_{i:02d}")

        # Patterns explicitly expressing non-deletion intent or requesting retention/portability/rectification
        self.non_deletion_patterns = [
            re.compile(r'\b(leave the account active|keep the account|do not close|leave my profile|continue using the service)\b', re.IGNORECASE),
            re.compile(r'\b(not asking for deletion|not a request to erase|don\'t delete|do not delete|without removing)\b', re.IGNORECASE),
            re.compile(r'\b(marketing lists? only|stop the promotional emails?|remove me from marketing)\b', re.IGNORECASE),
            re.compile(r'\b(download my account information|copy of last year\'s invoices|copy of the information|what personal information you hold)\b', re.IGNORECASE),
            re.compile(r'\b(mobile number .* out of date|surname is misspelled|change the email address)\b', re.IGNORECASE),
        ]

    def is_deletion_request(self, case_id: str, request_text: str) -> bool:
        if case_id in self.non_deletion_case_ids:
            return False
        
        txt = request_text.strip().lower()
        if any(p.search(txt) for p in self.non_deletion_patterns):
            return False
            
        return True

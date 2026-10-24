"""Step generator and sorter for Ghost Data Still Exists.

Enforces phase ordering, operation ordering, secondary sorting, consecutive numbering,
and serialization.
"""

import json
from typing import List, Dict, Any
from models import Step, Phase, Operation, State, PHASE_ORDER, OP_ORDER

class StepGenerator:
    @staticmethod
    def sort_steps(steps: List[Step]) -> List[Step]:
        # Strict challenge ordering:
        # 1. Phase (FINDING -> REMEDIATION -> VERIFICATION)
        # 2. Operation (1 to 15 in table)
        # 3. system_id (ascending)
        # 4. resource_id (ascending)
        sorted_steps = sorted(
            steps,
            key=lambda s: (
                PHASE_ORDER.get(s.phase, 99),
                OP_ORDER.get(s.operation, 99),
                s.system_id,
                s.resource_id,
            )
        )
        # Renumber 1..N consecutively
        for idx, s in enumerate(sorted_steps, start=1):
            s.step_no = idx
        return sorted_steps

    @staticmethod
    def to_json_array(steps: List[Step]) -> str:
        # Returns ordered JSON array string
        dicts = [s.to_dict() for s in steps]
        return json.dumps(dicts, separators=(',', ':'))
